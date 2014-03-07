AxiomsDef
=========



This is my native python implementation of a programming language I wrote. To use run axioms.py

To see an implementation done as a webapp using Google App Engine, go to:
http://webaxioms.appspot.com/ 

Functions and Predicates are defined in the following form.

<function(x1,...xn) 
all x1: .... all xn: P(i) -> function(x1,...xn) = expresion(m) 
... 
all x1: .... all xn: P(j) -> function(x1,...xn) = expresionm(k)< 

where n, m, i, j, k are arbitrary positive integers and expresion(X) is the Xth valid expresion implementation of some effective ordering 


<predicate(x1,...xn) 
all x1: .... all xn: P(i) -> predicate(x1,...xn) 
... 
all x1: .... all xn: P(j) -> predicate(x1,...xn) <-> P(k)< 

where n, m, i, j, k are arbitrary positive integers and P(X) is the Xth predicate implementation of some effective ordering 


functions and predicates implementations can be called with the following form: function(x1,...xn), predicate(x1,...xn) 
where n, m, i, j, k are arbitrary positive integers and P(x) is the xth predicate implementation of some effective ordering 

lists can be defined with the following form

L := [x1,...,xn] where n is an arbitrary positive integer, 

a valid expresion is any valid arithmatic expresion limited to the operators: + - * ^ = => = < > < ++ (list append) not and or and can include function calls, integers, and boolean literals 

the interpreter at this moment expects perfect input and does little to provide insight as to what may be wrong. 

