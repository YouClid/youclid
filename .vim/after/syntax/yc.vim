" Case insensitive matching
syntax case ignore

" Match any character that isn't a \ which is followed by a [ which delimits
" the start of one of our markups.
syn region YouclidText matchgroup=YouclidMarker start="[^\\]\[" end="\]" contains=YouclidKeyword keepend nextgroup=YouclidKeyword
" The above regex doesn't play nice with tags on the start of lines, and
" trying to do a 0 or 1 match using \= doesn't work for whatever reason. So we
" just add another thing that will match, which is the start of a line
" followed by a bracket
syn region YouclidText matchgroup=YouclidMarker start="^\[" end="\]" contains=YouclidKeyword keepend nextgroup=YouclidKeyword
syn keyword YouclidKeyword contained point line circle center loc step triangle definitions nextgroup=YouclidName
syn region YouclidName matchgroup=YouclidMarker start=' ' end="[ \]]" contained

" Youclid Customizations
hi link YouclidKeyword type
hi link YouclidMarker preproc
hi link YouclidText identifier
hi link YouclidName label
