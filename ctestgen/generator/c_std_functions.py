from ctestgen.generator import Function, Var, Pointer, SizeT, Void

malloc = Function('malloc', Pointer(Void), [Var('size', SizeT)])

free = Function('free', Void, [Var('ptr', Pointer(Void))])
