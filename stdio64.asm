
;------------int strLen(cadena) --------------
strLen:
		push rsi ;resguardar en pila rsi
		mov rsi, rax
sigChar:
	cmp byte[rax], 0
	jz finStrlen
	inc rax
	jmp sigChar
finStrLen:
		sub rax, rsi
		pop rsi ;restauro el contenido precio de rsi
		ret


;---------------printStr(cadena)
printStr:
		;resguardar regitros en pila		
		push rdx
		push rsi 
		push rdi
		push rax

		;--------------llamada a longitud de cadena (cadena en rax)
		call strLen
		;---------------la longitud se devuelve en rax

		mov rdx, 12 
		mov rsi, msg
		mov rdi, 1
		mov rax, 1 
		syscall 
		;----------------------devolver el contenido a los registros
		pop rdi 
		pop rsi 
		pop rdx
		ret

		;------------- void salir()
salir:
		mov rax, 60
		xor rdi, rdi
		syscall

		
