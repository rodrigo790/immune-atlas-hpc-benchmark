nextflow.enable.dsl=2

params.smoke_counts = null

process BENCHMARK {
    publishDir 'output', mode: 'copy'
    cpus 4
    input:
    path analysis
    path inputs
    output:
    path 'results'
    script:
    """
    mkdir -p data
    python analysis.py
    """
}

process CHECK_WORKER {
    cpus 1
    input:
    path analysis
    path inputs
    path counts
    output:
    path 'worker.json'
    script:
    """
    python analysis.py worker "$counts" 64 1 > worker.json
    python -c "import json; x=json.load(open('worker.json')); assert len(x[3]) == 12 and x[2] > 0"
    """
}

workflow {
    analysis = file("${projectDir}/analysis.py")
    inputs = file("${projectDir}/inputs.py")
    if (params.smoke_counts) {
        CHECK_WORKER(analysis, inputs, file(params.smoke_counts, checkIfExists: true))
    } else {
        BENCHMARK(analysis, inputs)
    }
}
