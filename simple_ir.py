from llvmlite import binding as llvm
from llvmlite import ir

CODE = """
def func() -> i32:
    return 42

def func2(a: i32) -> i32:
    b: i32 = 42
    return a*2 + b

func()
func2()

"""

module = ir.Module(name="my_module")
func_type = ir.FunctionType(ir.IntType(32), [])
func = ir.Function(module, func_type, name="func")

block = func.append_basic_block(name="entry")
builder = ir.IRBuilder(block)
builder.ret(ir.Constant(ir.IntType(32), 42))
builder.position_at_end(block)
# print(func)

func2_type = ir.FunctionType(ir.IntType(32), [ir.IntType(32)])
func2 = ir.Function(module, func2_type, name="func2")
block = func2.append_basic_block(name="entry")
builder = ir.IRBuilder(block)
# var_pointer = ir.AllocaInstr("b", ir.IntType(32), 1, name="b")
b = builder.alloca(ir.IntType(32), name="b")
builder.store(ir.Constant(ir.IntType(32), 42), b)
builder.ret(
    builder.add(
        builder.mul(func2.args[0], ir.Constant(ir.IntType(32), 2)),
        builder.load(b),
    )
)
builder.position_at_end(block)

# optimization
mod = llvm.parse_assembly(str(module))
print(mod)
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

# 2. Create the TargetMachine (tm)
# This grabs the default triple for the machine you are running on.
target = llvm.Target.from_default_triple()
tm = target.create_target_machine()
pto = llvm.create_pipeline_tuning_options(speed_level=3)
pass_builder = llvm.create_pass_builder(tm, pto)
pm = pass_builder.getModulePassManager()
pm.run(mod, pass_builder)
print("# OPTIMIZED: ")
print(mod)
