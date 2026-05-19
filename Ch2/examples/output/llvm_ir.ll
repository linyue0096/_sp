; SimpleLang -> LLVM IR
; Module

define i32 @main() {
  %x = add i32 0, 10
  %y = add i32 0, 20
  %t0 = icmp slt i32 %x, %y
  br i1 %t0, label %L0, label %L0_else
  ret i32 %x
  br label %L1
L0:
  ret i32 %y
L1:
  ret i32 0
  ret i32 %t1
  %t1 = icmp slt i32 %n, 1
  br i1 %t1, label %L2, label %L2_else
  ret i32 %n
  br label %L3
L2:
L3:
  %t2 = call i32 @fib()
  %t3 = call i32 @fib()
  ret i32 %t7
  ret i32 0
}
