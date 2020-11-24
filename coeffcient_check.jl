using Yao, YaoExtensions
using SymPy
@vars θ1 θ2 θ3

prep=chain(put(2,1=>Ry(θ1)),cnot(1,2),put(2,2=>Ry(θ2)),cnot(2,1),put(2,1=>Ry(θ3)))

(prep|>mat)*[1;0;0;0]