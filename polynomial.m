		 entry               % Start here
		 addi r14,r0,topaddr % Define top of the stack in case we need to print later
 sub     r1,r1,r1            % Reset the value of register 1
 addi    r1,r1,1             % Add the content of the value into register 1
 sw      counter(r0),r1      % Store that value in the address of counter
		 hlt                 % All done
 buf     res 20              % Buffer reservation in case printing to console is needed
 a       res 8               % Reserve variable a
 b       res 8               % Reserve variable b
 a       res 8               % Reserve variable a
 b       res 8               % Reserve variable b
 c       res 8               % Reserve variable c
 f1      res 16              % Reserve variable f1
 f2      res 24              % Reserve variable f2
 counter res 4               % Reserve variable counter
