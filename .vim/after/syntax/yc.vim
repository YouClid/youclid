syn region YouclidText start="[^\\]\=`" end="`" contains=YouclidKeyword,YouclidDelimeter keepend nextgroup=YouclidKeyword
syn keyword YouclidKeyword contained point line circle center loc step triangle nextgroup=YouclidName
syn region YouclidName matchgroup=YouclidText start=' ' end="[ `]" contained

" Youclid Customizations
hi YouclidKeyword ctermfg=220 ctermbg=NONE cterm=NONE guifg=#f1c40f guibg=NONE gui=NONE
hi YouclidText ctermfg=62 ctermbg=NONE cterm=NONE guifg=#6c71c4 guibg=NONE gui=NONE
hi YouclidName ctermfg=167 ctermbg=NONE cterm=NONE guifg=#e74c3c guibg=NONE gui=bold
