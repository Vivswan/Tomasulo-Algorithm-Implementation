TOMASULO_DEFAULT_PARAMETERS = {
    "num_register": 32,
    "num_rob": 128,
    "num_cbd": 1,

    "nop_latency": 1,
    "nop_unit_pipelined": 1,

    "integer_adder_latency": 1,
    "integer_adder_rs": 5,
    "integer_adder_pipelined": 0,

    "float_adder_latency": 3,
    "float_adder_rs": 3,
    "float_adder_pipelined": 1,

    "float_multiplier_latency": 20,
    "float_multiplier_rs": 2,
    "float_multiplier_pipelined": 1,

    "memory_unit_latency": 1,
    "memory_unit_ram_latency": 4,
    "memory_unit_queue_latency": 1,
    "memory_unit_ram_size": 1024,
    "memory_unit_queue_size": 8,
}
