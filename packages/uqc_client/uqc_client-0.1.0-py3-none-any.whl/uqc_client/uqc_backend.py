# -*- coding: utf-8 -*-
# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2018.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# Copyright 2025 UnitQC, Inc. (www.UnitQC.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""UnitQC 后端打包为qiskit后端"""
from __future__ import annotations

import time
import warnings
import logging
from typing import TypeVar, Union, List, Optional
from IPython.display import clear_output

from math import pi
from qiskit import QuantumCircuit
from qiskit.circuit import Measure, Parameter
from qiskit.circuit.library import RXGate, RYGate, RZGate, RGate, RZZGate, RXXGate, RYYGate
from qiskit.providers import BackendV2
from qiskit.providers import Options
from qiskit.transpiler import Target, CouplingMap, InstructionProperties
from qiskit.qasm3 import dumps
from qiskit.result import Result

from .uqc import UQC
from .uqc_interfaces import convert_artiq_result, merge_results, UQCFakeJob

logger = logging.getLogger(__name__)

# 定义变量类型
TargetT = TypeVar("TargetT", bound=Target)
CircuitsT = TypeVar("CircuitT", bound=Union[QuantumCircuit, List[QuantumCircuit]])


class UQCBackend(BackendV2):
    """
    UnitQC Backend 类。用于链接UQC后端对象，提交任务和返回结果。

    Parameters
    ----------
    token : str
        用于链接UQC后端对象的token。
    """

    def __init__(self, token: Optional[str] = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Connect to UQC backend instance
        self._init_client(token)
        self.gen_target_config()

    def _init_client(self, token: str):
        """
        初始化或者更新/重连UQC后端。

        Parameters
        ----------
        token : str
            用于 UQC() 后端的token.
        """
        self.uqc_client = UQC(token)

    @property
    def client(self) -> UQC:
        """
        返回 UQC 客户端实例。
        """
        return self.uqc_client

    def gen_target_config(self):
        """
        从UQC后端(self.uqc)读取相关信息，生成qiskit后端所需的Target对象。使用self.uqc.get_chip_info()读取。
        !!! 默认情况 ： coupling_map为全连接拓扑，目前未定义相关信息。
        """
        chip_info = self.uqc_client.get_chip_info()["QuantumChipArch"]
        self._n_qubits = chip_info["QubitCount"]
        self._max_shots = chip_info["MaxShots"]
        self._basis_gates = chip_info["BasicQGate"]
        # 定义全连接拓扑
        self._coupling_map = CouplingMap(
            couplinglist=[[i, j] for i in range(self._n_qubits) for j in range(self._n_qubits) if i < j]
        )

        # 创建 Target
        self._target = Target()
        theta = Parameter("θ")
        phi = Parameter("Φ")

        # 定义硬件适配门集
        gate_classes = {
            "rx": RXGate(theta),
            "ry": RYGate(theta),
            "rz": RZGate(theta),
            "r": RGate(theta, phi),
            "rxx": RXXGate(pi / 2),
            "ryy": RYYGate(pi / 2),
            "rzz": RZZGate(pi / 2),
        }

        # 在Target中注册相应的门
        for name in self._basis_gates:
            gate = gate_classes[name]
            prop_dict = {}

            # 对每个门按照拓扑注册，单比特门（rx，ry，rz，r）在每个qubit上, 两比特门（rxx，ryy，rzz）在coupling_map上
            if name in ["rx", "ry", "rz", "r"]:
                for i in range(self._n_qubits):
                    prop_dict[(i,)] = InstructionProperties()
            elif name in ["rxx", "ryy", "rzz"]:
                for ctrl, tgt in self._coupling_map.get_edges():
                    prop_dict[(ctrl, tgt)] = InstructionProperties()
                    prop_dict[(tgt, ctrl)] = InstructionProperties()  # 对称的门

            self._target.add_instruction(gate, properties=prop_dict)
        self._target.add_instruction(
            Measure(), properties={(i,): InstructionProperties() for i in range(self._n_qubits)}
        )

    @classmethod
    def _default_options(cls) -> Options:
        return Options(
            shots=100,
            # sampler_seed=None,
            # noise_model="ideal",
            error_mitigation=None,
        )

    @property
    def options(self) -> Options:
        return self._options

    @property
    def target(self):
        return self._target

    @property
    def num_qubits(self):
        return self._n_qubits

    @property
    def coupling_map(self):
        return self._coupling_map

    def check_circuit_ops(self, circuit: QuantumCircuit) -> bool:
        """
        检查是否输入线路里的门都受硬件后端对应的Target支持。
        !!! 初步方法，未检查门作用的qubit序号。

        Parameters
        ----------
        circuit : QuantumCircuit
            待验证的线路。

        Returns
        -------
        bool
            True 如果所有操作都受支持， 反之False。

        Raises
        ------
        ValueError
            如果存在不受支持的线路。
        """
        unsupported_ops = []
        for instr, qargs, cargs in circuit.data:
            opname = instr.name
            if opname not in self._target:
                unsupported_ops.append(opname)

        if unsupported_ops:
            raise ValueError(f"Unsupported operations found: {set(unsupported_ops)}")
            return False

        return True

    def run_single_circuit(self, circuit: QuantumCircuit, has_check: bool = False, **kwargs) -> Result:
        """
        使用已连接的UQC后端(self.uqc)运行！一个已编译！的qiskit线路，返回结果转换为qiskit Result类。

        Parameters
        ----------
        circuit : QuantumCircuit
            待运行线路。必须是已编译的。
        has_check : bool
            如果为True，使用self.check_circuit_ops()检查输入线路是否合法。

        Returns
        -------
        result : qiskit.result.result.Result
            将self.uqc.get_task_result()返回的结果转换得到的qiskit的Result类。

        """

        # 检查线路操作是否合法
        if has_check:
            self.check_circuit_ops(circuit)

        # 转换线路为OpenQASM并提交任务
        qasm_str = dumps(circuit)
        self.uqc_client.submit_task(convert_qprog=qasm_str, target="Matrix2", shots=kwargs["shots"])

        # 查询运行状态直到运行成功或失败
        while True:
            status = self.uqc_client.get_task_status()
            clear_output(wait=True)
            tmp = f"Status [{time.strftime('%H:%M:%S')}]: {status}"
            if "circ_num" in kwargs:
                circ_num = kwargs["circ_num"]
                tmp = f"Circuit {circ_num} Status [{time.strftime('%H:%M:%S')}]: {status}"
            logger.info(tmp)

            if status == "SUCCESS" or status == "FAILURE":
                break
            time.sleep(1)

        # 运行失败
        if status == "FAILURE":
            raise RuntimeError("Circuit excution failed.")

        # 运行成功
        if status == "SUCCESS":
            result = self.uqc_client.get_task_result()
            result = convert_artiq_result(result)
            return result

    # pylint: disable=missing-type-doc,missing-param-doc,arguments-differ,arguments-renamed
    def run(self, circuits: CircuitsT(QuantumCircuit), **kwargs) -> UQCFakeJob:
        """
        输入线路（列表），在UQC后端上运行并返回结果。如果未输入shots，则使用默认配置的shots。

        Parameters
        ----------
        circuit : qiskit.circuit.quantumcircuit.QuantumCircuit or List[qiskit.circuit.quantumcircuit.QuantumCircuit]
            一个或者一个列表的QuantumCircuit对象。

        Returns
        -------
        UQCFakeJob
            一个UQCFakeJob（qiskit的JobV1的子类）对象，包含运行的线路和运行结果等信息。
        """
        # 线路检查：是否有测量，是否使用某选项
        if not all((self.has_valid_mapping(circ) for circ in (circuits if isinstance(circuits, list) else [circuits]))):
            warnings.warn(
                "Circuit is not measuring any qubits",
                UserWarning,
                stacklevel=2,
            )

        for kwarg in kwargs:
            if not hasattr(self.options, kwarg):
                warnings.warn(
                    f"Option {kwarg} is not used by this backend",
                    UserWarning,
                    stacklevel=2,
                )
        # 如果未输入shots则使用默认配置
        if "shots" not in kwargs:
            kwargs["shots"] = self.options.shots

        # 运行线路或线路列表
        if isinstance(circuits, QuantumCircuit):
            results = [self.run_single_circuit(circuits, **kwargs)]
        elif isinstance(circuits, list) and all(isinstance(circ, QuantumCircuit) for circ in circuits):
            results = []
            for i, circuit in enumerate(circuits):
                results += [self.run_single_circuit(circuit, circ_num=i, **kwargs)]

        # 合并结果列表，转换为UQCFakeJob类
        results = merge_results(results)
        return UQCFakeJob(self, results)

    def has_valid_mapping(self, circuit: QuantumCircuit) -> bool:
        """
        检查线路是否至少存在一个qubit到经典bit的测量。

        Parameters
        ----------
        circuit : qiskit.circuit.QuantumCircuit
            待检查线路。

        Returns
        -------
        bool
            True如果有，False反之。
        """
        # 检查是否有qubit被测量
        for instruction, _, cargs in circuit.data:
            if instruction.name == "measure" and len(cargs):
                return True
        # 如果没有，返回False
        return False

    def make_initial_layout_middle(self, num_qubits: int) -> List[int]:
        """
        选择一组靠中间的物理qubit作为编译时的initial_layout。
        例子： self._n_qubits=9, num_qubits=3 -> [3, 4, 5].

        Parameters
        ----------
        num_qubits : int
            待编译线路使用的qubit数目。

        Returns
        -------
        List[int]
            一个列表，用于`transpile(..., initial_layout=returned_list)`.

        Raises
        ------
        ValueError
            如果num_qubits不在 [1, self._n_qubits]内。
        """
        N = getattr(self, "_n_qubits", None)
        if not isinstance(N, int):
            raise ValueError("Backend is missing `_n_qubits` integer attribute.")
        if not (1 <= num_qubits <= N):
            raise ValueError(f"`num_qubits` must be in [1, {N}], got {num_qubits}.")

        start = (N - num_qubits) // 2
        return list(range(start, start + num_qubits))

    @property
    def max_circuits(self) -> int:
        """
        单个任务内可运行的线路最大数量。BackendV2要求定义的方法。
        如果没有上限，返回None

        Returns
        -------
        int
            可运行的线路最大数量。
        """
        return 50

    # @abc.abstractmethod
    # def with_name(self, name, **kwargs) -> UQCBackend:
    #     """Helper method that returns this backend with a more specific target system."""
    #     pass

    # @abc.abstractmethod
    # def gateset(self) -> Literal["qiskit", "native_msxx", "native_mszz", "native_mszz_vz"]:
    #     """Helper method returning the gateset this backend is targeting."""
    #     pass

    # def __eq__(self, other) -> bool:
    #     if isinstance(other, self.__class__):
    #         return self.name() == other.name() and self.gateset() == other.gateset()
    #     else:
    #         return False

    # def __ne__(self, other) -> bool:
    #     return not self.__eq__(other)
