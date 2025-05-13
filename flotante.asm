;Manejo de valores e coma flotante
;creador;abemen
;fecha: 21 abr 2025
; compilar: as -arch arm64 flotante.asm -o flotante.o
;link: gcc flotante.o -o flotante

extern printf

SECTION .data
	pi:						dq 		3.14159
	diametro 			dq		5.0
	format				dq		"C = ¶*d = %f * % f = %f", 10,0

SECTION .bss
	C:						resq			1

SECTION .text 
	global main 

main:
	push		rbp
	fld			qword [diametro] 			;carga el radio al registro ST0
	fmul		qword [pi]						;diametro * pi
	fstp		qword [C]							;guarda el resultado en ST0 en C
	;------------------------------- llamada a print f ----------------------------
	
	mov			rdi, format 					;cargar la cadena formateada
	movq		xmm0, qword [pi] 
	movq		xmm1, qword [diametro]
	movq		xmm2, qword [C]
	mov			rax, 3
	call		printf

	pop			rbp


	mov			rax, 1
	xor			rbx, rbx
	int			80h
		