import rtopy as rp


# an R function that returns the product of an arbitrary number of arguments 
# notice the double braces around the R function's code
# and the a semi-colon (';') after each instruction
r_code1 = f"""my_func <- function(arg1=NULL, arg2=NULL, arg3=NULL, arg4=NULL, arg5=NULL) {{
                args <- c(arg1, arg2, arg3, arg4, arg5);
                args <- args[!sapply(args, is.null)];
                result <- prod(args);
                return(result)
              }}
              """              

# an R function that returns the sum of an arbitrary number of arguments 
r_code2 = f"""my_func <- function(arg1=NULL, arg2=NULL, arg3=NULL, arg4=NULL, arg5=NULL) {{
            args <- c(arg1, arg2, arg3, arg4, arg5);
            args <- args[!sapply(args, is.null)];
            result <- sum(args);
            return(result)
          }}
         """    

# an R function that returns a list of vectors 
r_code3 = f"""my_func <- function(arg1, arg2) {{                  
            list(x = mtcars[, 'mpg'], y = mtcars[, arg1], z = mtcars[, arg2])
          }}
         """

# an R function that returns a vector 
r_code4 = f"""my_func <- function(arg1=NULL, arg2=NULL, arg3=NULL) {{
            args <- c(arg1, arg2, arg3);
            args <- args[!sapply(args, is.null)];
            print(args);
            return(as.vector(args))
          }}
         """

# an R function that returns a list of matrices 
# won't work for named rows
r_code5 = f"""my_func <- function(arg1, arg2) {{   
            X <- as.matrix(mtcars);
            colnames(X) <- NULL; 
            rownames(X) <- NULL;            
            list(x = X[, 1], y = X[, c(arg1, arg2)])
          }}
         """

# an R function that returns a list of vector, matrix and scalar
r_code6 = f"""my_func <- function(arg1, arg2) {{   
            X <- as.matrix(mtcars);
            colnames(X) <- NULL; 
            rownames(X) <- NULL;            
            list(x = X[, 1], y = X[, c(arg1, arg2)], z = 5)
          }}
         """

# an R function that returns a matrix
r_code7 = f"""my_func <- function(arg1, arg2) {{   
            X <- as.matrix(mtcars);
            colnames(X) <- NULL; 
            rownames(X) <- NULL;            
            return(x = X[1:3, c(arg1, arg2)])
          }}
         """


print(rp.callfunc(r_code=r_code1, type_return="int", arg1=3, arg2=5, arg3=2))
print(rp.callfunc(r_code=r_code2, type_return="float", arg1=1.5, arg2=2.5, arg4=4.5))
print(rp.callfunc(r_code=r_code2, type_return="float", arg1=3.5, arg3=5.3, arg4=4.2))
print("\n -------------------------------------------------- \n")
res = rp.callfunc(r_code=r_code3, type_return="dict", arg1=2, arg2=3)
print(res)
print("-----------------------")
res2 = rp.callfunc(r_code=r_code3, type_return="dict", arg1="cyl", arg2="disp")
print(res2)
print("-----------------------")
res3 = rp.callfunc(r_code=r_code3, type_return="dict", arg1="cyl", arg2=3)
print(res3)
print("-----------------------")
res4 = rp.callfunc(r_code=r_code5, type_return="dict", arg1=2, arg2=3)
print(res4)
print("\n -------------------------------------------------- \n")
print(rp.callfunc(r_code=r_code4, type_return="list", arg1=3.5, arg2=5.3))
print(rp.callfunc(r_code=r_code4, type_return="list", arg1=3.5, arg2=5.3, arg3=4.1))
print("\n -------------------------------------------------- \n")
res5 = rp.callfunc(r_code=r_code6, type_return="dict", arg1=2, arg2=3)
print(res5)
print("\n -------------------------------------------------- \n")
res6 = rp.callfunc()
print(res6)
print("\n -------------------------------------------------- \n")
res7 = rp.callfunc(r_code=r_code7, type_return="list", arg1=2, arg2=3)
print(res7)
