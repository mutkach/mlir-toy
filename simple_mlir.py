from mlir.ir import Context, Module, InsertionPoint, Location, IntegerType
from mlir.dialects import arith, affine, tensor

with Context() as ctx, Location.unknown():
    module = Module.create()
    i32 = IntegerType.get_signless(32)
    with InsertionPoint(module.body):
        c = arith.constant(i32, 42)
    print(module)

