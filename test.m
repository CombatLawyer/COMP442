		 entry               % Start here
 a       res 4               % Reserve variable a
 b       res 4               % Reserve variable b
 sub     r1,r1,r1            % Reset the value of register 1
 addi    r1,r1,8             % Add the content of the value into register 1
 sw      a(r0),r1            % Store that value in the address of a
