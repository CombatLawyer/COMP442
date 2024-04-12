        	   entry               % Start here
         addi    r14,r0,topaddr      % Define top of the stack in case we need to print later
         sub     r1,r1,r1            % Reset the value of register 1
         addi    r1,r1,1             % Add the content of the value into register 1
         sw      a(r0),r1            % Store that value in the address of a
         sub     r1,r1,r1            % Reset the value of register 1
         addi    r1,r1,9             % Add the content of the value into register 1
         sw      b(r0),r1            % Store that value in the address of b
swhile1  lw      r1,b(r0)            % We are loading b into r1
         lw      r2,a(r0)            % We are loading a into r2
         cgt     r3,r1,r2            % Check the condition comapering both terms
         sw      tn1(r0),r3          % Value of the result will be stored here
         lw      r1,tn1(r0)          % We are loading tn1 into r1
         bz      r1,ewhile1          % Send the code to the end while block if condition false
         lw      r1,a(r0)            % We are loading a into r1
         sw      -8(r14),r1          % Placing a onto the top of the stack
         addi    r1,r0,buf           % Load the buffer on the stack
         sw      -12(r14),r1         % Load the buffer on the stack
         jl      r15,intstr          % Calling intstr subroutine from lib.m
         sw      -8(r14),r13         % Retrieve output of intstr and place where putstr expects it
         jl      r15,putstr          % Calling putstr subroutine from lib.m to print to console
         lw      r1,a(r0)            % We are loading a into r1
         addi    r2,r1,1             % Add the number to r1
         sw      t1(r0),r2           %  Store the result in the intermediate
         lw      r1,t1(r0)           % Load the variable into r1
         sw      a(r0),r1            % Store the variable into a
         j       swhile1             % Skip the next code block if condtional was true
ewhile1  sub     r1,r1,r1            % Reset the value of register 1
         sub     r2,r2,r2            % Reset the value of register 2
         addi    r1,r1,13            % Add the integer portion of the float into register 1
         sw      f(r2),r1            % Store that value in the the first 8 bytes of f
         addi    r2,r2,8             % Shift the offset by 8 bits
         sub     r1,r1,r1            % Reset the value of register 1
         addi    r1,r1,8             % Add the decimal portion of the float into register 1
         sw      f(r2),r1            % Store that value in the the last 8 bytes of f
         lw      r1,f(r0)            % We are loading f into r1
         sw      -8(r14),r1          % Placing f onto the top of the stack
         addi    r1,r0,buf           % Load the buffer on the stack
         sw      -12(r14),r1         % Load the buffer on the stack
         jl      r15,intstr          % Calling intstr subroutine from lib.m
         sw      -8(r14),r13         % Retrieve output of intstr and place where putstr expects it
         jl      r15,putstr          % Calling putstr subroutine from lib.m to print to console
         sub     r2,r2,r2            % Reset the value of register 2
         addi    r2,r2,8             % Add the offset of the value into register 2
         lw      r1,f(r2)            % We are loading f into r1
         sw      -8(r14),r1          % Placing f onto the top of the stack
         addi    r1,r0,buf           % Load the buffer on the stack
         sw      -12(r14),r1         % Load the buffer on the stack
         jl      r15,intstr          % Calling intstr subroutine from lib.m
         sw      -8(r14),r13         % Retrieve output of intstr and place where putstr expects it
         jl      r15,putstr          % Calling putstr subroutine from lib.m to print to console
        	   hlt                 % All done
         buf     res 20              % Buffer reservation in case printing to console is needed
         a       res 4               % Reserve variable a
         b       res 4               % Reserve variable b
         c       res 28              % Reserve variable c
         f       res 8               % Reserve variable f
         t1      res 4               % Reserve memory for the intermediate parameter
         tn1     res 4               % Reserve memory for the temp variable used to contain the result of the conditional