"""UnitQC 后端输入/输出-qiskit接口"""
from typing import List

from qiskit import transpile, QuantumCircuit
from qiskit.result import Result
from qiskit.providers.job import JobV1
from qiskit.providers import JobStatus
from qiskit.converters import circuit_to_dag

import uuid


def quantum_circuit_to_list(qc : QuantumCircuit, is_parallelized : bool =True) -> List:
    """
    返回编译线路的操作list。

    Parameters
    ----------
    qc : qiskit.circuit.quantumcircuit.QuantumCircuit
        编译后的线路，只包含rphi和ms门。
    is_parallelized : bool
        表示操作list是否并行。
    Returns
    -------
    c_list : list
        所需的操作list。

    Raises
    ------
    ValueError 
        如果不受支持的门在输入线路中。
    """
    c_list = []

    dag = circuit_to_dag(qc)
    for layer in dag.layers():
        current_layer = []
        for node in layer['graph'].nodes():
            if hasattr(node, 'op'):
                op = node.op

                if op.name == "measure":
                    continue
                elif op.name == "rphi":
                    qubits = tuple([qc.find_bit(qubit)[0] for qubit in node.qargs])
                    theta, phase = op.params
                    operation = {"gate": "R", "qubit_index": qubits, "theta": theta, "phase": phase}
                    current_layer.append(operation)
                elif op.name == "ms":
                    qubits = tuple([qc.find_bit(qubit)[0] for qubit in node.qargs])
                    operation = {"gate": "MS", "qubit_index": qubits}
                    current_layer.append(operation)
                else:
                    raise ValueError('Unsupported gate: "%s"' % op.name)
                    
        if current_layer:
            c_list.append(current_layer)

    c_list_flattened = [[op] for layer in c_list for op in layer]
    if not is_parallelized:
        c_list = c_list_flattened.copy()
        
    return c_list
    

def convert_artiq_result(artiq_result : List) -> Result:
    """
    转换ARTIQ测控系统返回的结果为qiskit.result.result.Result类。

    Parameters
    ----------
    artiq_result : list 
        ARTIQ的结果list

    Returns
    -------
    result : qiskit.result.result.Result 
        对应的Result类，支持get_counts()方法。
    """
    artiq_result_dict = artiq_result[0]
    
    backend_name = "Matrix2"
    backend_version = artiq_result_dict['artiq_version']
    qobj_id = None
    job_id = artiq_result_dict['rid']
    success = True
    
    # 删除expid条目中非法元素（无法被eval取值）
    tmp=artiq_result_dict['expid']
    before, _, rest = tmp.partition('"points_info"')
    _, _, after = rest.partition('")}],')
    tmp = before + after
    before, _, after = tmp.partition('"is_circuit": true,')
    tmp = before + after

    expid = eval(tmp)

    # 检查数据合法性
    if not (all(len(sublist) > 0 and (len(sublist) & (len(sublist) - 1) == 0) for sublist in artiq_result_dict['datasets']['computational_basis_histogram'])):
        raise ValueError("Incorrect measurement result counts")

    # 收集计数，打包成Dict
    n = int(len(artiq_result_dict['datasets']['computational_basis_histogram']).bit_length() - 1)
    data = {
        'counts':
            {
                format(int(k), f'0{n}b'): v for k, v in artiq_result_dict['datasets']['computational_basis_histogram']
            }
    }
    
    results = [
        {
            'shots': expid['arguments']['repeat'],
            'success': success,
            'data': data
        } 
    ]

    result = Result.from_dict(
        {
            'backend_name': backend_name,
            'backend_version': backend_version,
            'qobj_id': qobj_id,
            'job_id': job_id,
            'success': success,
            'results': results
        }
    )

    return result

def merge_results(result_list : List[Result]) -> Result:
    """
    把几个qiskit.result.result.Result类合并成一个。对于共通的信息，选用第一个的。

    Parameters
    ----------
    result_list : list of qiskit.result.Result
        用于合并的Result对象列表。为了确保一致性，所有Result对象都应该来自于同一个后端backend。

    Returns
    -------
    qiskit.result.Result
        一个新的Result对象，包含所有Result对象的"result"字典值。

    Raises
    ------
    ValueError
        如果输入list是空的。
    """
    if not result_list:
        raise ValueError("No results to merge")

    # 使用第一个Result对象作为模板
    base_dict = result_list[0].to_dict()

    # 收集所有Result对象的结果计数，即字典值"results"。
    merged_results = []
    for r in result_list:
        merged_results.extend(r.to_dict()["results"])

    base_dict["results"] = merged_results

    # 返回一个所需的Result对象
    return Result.from_dict(base_dict)
    

class UQCFakeJob(JobV1):
    """
    初始化UQCFakeJob类。使用.result().get_counts()方法得到结果计数。

    Parameters
    ----------
    backend : qiskit.providers.BackendV2 子类
        JobV1类必要信息。
    result : qiskit.result.result.Result 子类
        JobV1类必要信息，作为该Job的运行结果。

    """
    def __init__(self, backend, result : Result):
        job_id = str(uuid.uuid4())  # random job ID
        super().__init__(backend, job_id)
        self._result = result

    def submit(self):
        pass

    def result(self):
        return self._result

    def status(self):
        return JobStatus.DONE

    def cancel(self):
        pass

    def done(self):
        return True

    def running(self):
        return False

    def cancelled(self):
        return False