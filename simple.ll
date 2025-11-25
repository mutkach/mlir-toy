; ModuleID = '<string>'
source_filename = "<string>"
target triple = "unknown-unknown-unknown"

define i32 @func() {
entry:
  ret i32 42
}

define i32 @func2(i32 %.1) {
entry:
  %b = alloca i32, align 4
  store i32 42, ptr %b, align 4
  %.4 = mul i32 %.1, 2
  %.5 = load i32, ptr %b, align 4
  %.6 = add i32 %.4, %.5
  ret i32 %.6
}

; OPTIMIZED: 
; ModuleID = '<string>'
source_filename = "<string>"
target triple = "unknown-unknown-unknown"

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define noundef i32 @func() local_unnamed_addr #0 {
entry:
  ret i32 42
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(none)
define range(i32 42, 41) i32 @func2(i32 %.1) local_unnamed_addr #0 {
entry:
  %.4 = shl i32 %.1, 1
  %.6 = add i32 %.4, 42
  ret i32 %.6
}

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(none) }

