" Case insensitive matching
syntax case ignore

" Match any character that isn't a \ which is followed by a [ which delimits
" the start of one of our markups.
syn region YouclidText matchgroup=YouclidMarker start="\\\@<!\[" end="\\\@<!\]" contains=YouclidKeyword keepend nextgroup=YouclidKeyword
syn keyword YouclidKeyword contained point line circle center loc step polygon clear nextgroup=YouclidName
syn region YouclidName matchgroup=YouclidMarker start=' ' end="[ \]]" contained

" Youclid Customizations
hi link YouclidKeyword type
hi link YouclidMarker preproc
hi link YouclidText identifier
hi link YouclidName label
