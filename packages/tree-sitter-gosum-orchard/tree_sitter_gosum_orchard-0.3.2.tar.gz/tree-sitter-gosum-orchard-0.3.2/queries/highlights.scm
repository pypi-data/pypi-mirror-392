[
  "alpha"
  "beta"
  "dev"
  "pre"
  "rc"
  "+incompatible"
] @keyword


(module_path) @string @text.uri
(module_version) @string.special

(hash_version) @attribute
(hash) @symbol

[
 (number)
 (number_with_decimal)
 (hex_number)
] @number

(checksum
  (go_mod) @string)

[
  ":"
  "."
  "-"
  "/"
] @punctuation.delimiter
