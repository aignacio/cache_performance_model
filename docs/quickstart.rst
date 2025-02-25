Quick Start Guide
=================

Basic Usage
-----------

Create a simple cache configuration::

    from cache_model import CacheSimulator

    # Create a 32KB L1 cache
    cache_config = {
        'size': 32768,
        'line_size': 64,
        'associativity': 8,
        'replacement_policy': 'LRU'
    }

    simulator = CacheSimulator(cache_config)
    simulator.simulate('memory_trace.txt')

Analyzing Results
-----------------

Get performance metrics::

    results = simulator.get_statistics()
    print(f"Hit Rate: {results['hit_rate']:.2f}%")
    print(f"Miss Rate: {results['miss_rate']:.2f}%")
    print(f"Average Access Time: {results['avg_access_time']:.2f} ns")

Visualization
-------------

Generate performance graphs::

    simulator.plot_hit_rate()
    simulator.plot_access_pattern()
