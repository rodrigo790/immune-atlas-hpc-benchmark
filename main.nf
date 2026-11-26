nextflow.enable.dsl=2
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
workflow {
    BENCHMARK(file("${projectDir}/analysis.py"), file("${projectDir}/inputs.py"))
}
