import click
from core.parser import Parser
from miner.generic.static.staticMinerContext import StaticMinerContext
from miner.generic.dynamic.dynamicMinerContext import DynamicMinerContext
from exporter.ymlExporter import YMLExporter

@click.group()
def cli():
    """
    Archminer generate an architectural model of a microservices application
    """

@cli.command()
@click.argument('strategy')
@click.argument('source')
@click.argument('target')
@click.option('--time', default = 60, help = 'Seconds of monitoring')
@click.option('--name', default = 'Generic application', help = 'Name of the microTOSCA model')
def generate(strategy, source, target, time, name):
    nodes = {}
    strategyConfig = Parser.searchMinerStrategy(strategy)
    if 'static' in strategyConfig:
        print('Executing static mining...')
        StaticMinerContext.doStaticMining(strategyConfig['static']['class'], source, strategyConfig['static']['args'] if 'args' in strategyConfig['static'] else {}, nodes)
    if 'dynamic' in strategyConfig:
        print('Executing dynamic mining...')
        if 'args' in strategyConfig['dynamic']:
            strategyConfig['dynamic']['args']['time'] = time
            DynamicMinerContext.doDynamicMining(strategyConfig['dynamic']['class'], source, strategyConfig['dynamic']['args'], nodes)
        else:
            strategyConfig['dynamic']['args'] = {'time': time}
            DynamicMinerContext.doDynamicMining(strategyConfig['dynamic']['class'], source, strategyConfig['dynamic']['args'], nodes)
    
    #REFINER

    print('Exporting microTOSCA...')
    YMLExporter.export(nodes, target, name)

if __name__ == "__main__":
    cli()
