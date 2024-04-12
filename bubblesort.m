		 entry               % Start here
		 addi r14,r0,topaddr % Define top of the stack in case we need to print later
 sub     r1,r1,r1            % Reset the value of register 1
 addi    r1,r1,0             % Add the content of the value into register 1
 sw      i(r0),r1            % Store that value in the address of i
 sub     r1,r1,r1            % Reset the value of register 1
 addi    r1,r1,0             % Add the content of the value into register 1
 sw      j(r0),r1            % Store that value in the address of j
 sub     r1,r1,r1            % Reset the value of register 1
 addi    r1,r1,0             % Add the content of the value into register 1
 sw      temp(r0),r1         % Store that value in the address of temp
 sub     r1,r1,r1            % Reset the value of register 1
 addi    r1,r1,0             % Add the content of the value into register 1
 sw      i(r0),r1            % Store that value in the address of i
		 hlt                 % All done
 buf     res 20              % Buffer reservation in case printing to console is needed
 n       res 4               % Reserve variable n
 i       res 4               % Reserve variable i
 j       res 4               % Reserve variable j
 temp    res 4               % Reserve variable temp
 n       res 4               % Reserve variable n
 i       res 4               % Reserve variable i
 arr     res 4               % Reserve variable arr
