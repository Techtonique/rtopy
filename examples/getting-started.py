import rtopy as rp


# an R function that returns the product of an arbitrary number of arguments 
r_func1 = f"""my_func <- function(arg1=NULL, arg2=NULL, arg3=NULL, arg4=NULL, arg5=NULL) {{
                args <- c(arg1, arg2, arg3, arg4, arg5);
                args <- args[!sapply(args, is.null)];
                result <- prod(args);
                return(result)
              }}
              """              

# an R function that returns the sum of an arbitrary number of arguments 
r_func2 = f"""my_func <- function(arg1=NULL, arg2=NULL, arg3=NULL, arg4=NULL, arg5=NULL) {{
            args <- c(arg1, arg2, arg3, arg4, arg5);
            args <- args[!sapply(args, is.null)];
            result <- sum(args);
            return(result)
          }}
         """    

# an R function that returns a list of vectors 
r_func3 = f"""my_func <- function(arg1, arg2) {{                  
            list(x = mtcars[, 'mpg'], y = mtcars[, arg1], z = mtcars[, arg2])
          }}
         """

# an R function that returns a vector 
r_func4 = f"""my_func <- function(arg1=NULL, arg2=NULL, arg3=NULL) {{
            args <- c(arg1, arg2, arg3);
            args <- args[!sapply(args, is.null)];
            print(args);
            return(as.vector(args))
          }}
         """

# an R function that returns a list of matrices 
r_func5 = f"""my_func <- function(arg1, arg2) {{   
            X <- as.matrix(mtcars);
            rownames(X) <- NULL;
            colnames(X) <- NULL;               
            list(x = X[, 1], y = X[, c(arg1, arg2)])
          }}
         """



print(rp.callfunc(r_func=r_func1, type_result="int", arg1=3, arg2=5, arg3=2))
print(rp.callfunc(r_func=r_func2, type_result="float", arg1=1.5, arg2=2.5, arg4=4.5))
print(rp.callfunc(r_func=r_func2, type_result="float", arg1=3.5, arg3=5.3, arg4=4.2))
print("\n -------------------------------------------------- \n")
res = rp.callfunc(r_func=r_func3, type_result="dict", arg1=2, arg2=3)
print(res['x'])
print(res['y'])
print(res['z'])
print("-----------------------")
res2 = rp.callfunc(r_func=r_func3, type_result="dict", arg1="cyl", arg2="disp")
print(res2['x'])
print(res2['y'])
print(res2['z'])
print("-----------------------")
res3 = rp.callfunc(r_func=r_func3, type_result="dict", arg1="cyl", arg2=3)
print(res3['x'])
print(res3['y'])
print(res3['z'])
print("-----------------------")
res4 = rp.callfunc(r_func=r_func5, type_result="dict", arg1=2, arg2=3)
print(res4['y'])
print("\n -------------------------------------------------- \n")
print(rp.callfunc(r_func=r_func4, type_result="list", arg1=3.5, arg2=5.3))
print(rp.callfunc(r_func=r_func4, type_result="list", arg1=3.5, arg2=5.3, arg3=4.1))

