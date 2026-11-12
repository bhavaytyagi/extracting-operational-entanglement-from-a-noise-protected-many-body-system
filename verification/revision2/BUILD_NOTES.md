# Writer build notes and preserved error trail — 2026-11-11

The first revision-builder run failed before writing a revised draft because its blank-line paragraph selector included the peripheral equation/next sentence. Its A1 boundary was changed to the explicit following align environment and the run then completed. No original source was changed.

The initial caption replacements used that paragraph selector and unintentionally consumed the figure closing tags before the next blank line. Root caught the error during compilation and mechanically restored only the missing closings in the separate integrated copy. The writer builder now uses balanced-brace caption selection, retaining all environment closings. A regenerated writer draft passes equal begin/end counts for figure, figure*, align and equation. This structural check is not a PDF compile or visual check.

The integrated source is owned by root for compilation; Manny did not edit it concurrently. The author-requested abstract/title hold remains, with one separately supplied last-sentence consistency fragment needed to avoid conflict with the finite-time body qualification. No length gate was used.
