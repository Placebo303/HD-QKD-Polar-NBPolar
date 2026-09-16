# Decode-reject advancement requirements

At K<45, `ImpossibleDisclosedValueError` SHALL record an intermediate rejected
decode, invoke no verification, count one public feedback request and advance
to the immediately next frozen level. At K45 it SHALL be terminal
`decode_failed`; non-whitelisted exceptions SHALL remain fail-closed. Every
retry SHALL discard prior decoder state and preserve the fixed order/K.

One fresh 300-block run SHALL compare static K45, strict-stop incremental and
decode-reject-advance on identical blocks with independently recountable
disclosure, feedback and verification.
