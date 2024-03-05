#!/usr/bin/env python

"""Tests for `rtopy` package."""


import unittest
from click.testing import CliRunner

import rtopy as rp 
from rtopy import cli


class TestRtopy(unittest.TestCase):
    """Tests for `rtopy` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_unique_return_value(self):

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
        res1 = rp.callfunc(r_code=r_code1, type_return="int", arg1=3, arg2=5, arg3=2)
        res2 = rp.callfunc(r_code=r_code2, type_return="float", arg1=1.5, arg2=2.5, arg4=4.5)
        res3 = rp.callfunc(r_code=r_code2, type_return="float", arg1=3.5, arg3=5.3, arg4=4.2)
        self.assertEqual(res1, 30)
        self.assertEqual(res2, 8.5)
        self.assertEqual(res3, 13)
        self.assertAlmostEqual(rp.callfunc(), -0.6264538)

    def test_list_return_value(self):
        # an R function that returns a vector 
        r_code4 = f"""my_func <- function(arg1=NULL, arg2=NULL, arg3=NULL) {{
                    args <- c(arg1, arg2, arg3);
                    args <- args[!sapply(args, is.null)];
                    print(args);
                    return(as.vector(args))
                }}
                """
        res1 = rp.callfunc(r_code=r_code4, type_return="list", arg1=3.5, arg2=5.3)
        res2 = rp.callfunc(r_code=r_code4, type_return="list", arg1=3.5, arg2=5.3, arg3=4.1)
        self.assertEqual(res1[0], 3.5)
        self.assertEqual(res2[0], 3.5)

    def test_dict_return_value(self):

        # an R function that returns a vector 
        # an R function that returns a list of vectors
        r_code3 = f"""my_func <- function(arg1, arg2) {{
            list(x = mtcars[, 'mpg'], y = mtcars[, arg1], z = mtcars[, arg2])
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
        res2 = rp.callfunc(r_code=r_code3, type_return="dict", arg1="cyl", arg2="disp")
        res3 = rp.callfunc(r_code=r_code3, type_return="dict", arg1="cyl", arg2=3)
        res4 = rp.callfunc(r_code=r_code5, type_return="dict", arg1=2, arg2=3)
        res5 = rp.callfunc(r_code=r_code6, type_return="dict", arg1=2, arg2=3)
        self.assertEqual(res2['x'][0], 21)
        self.assertEqual(res3['y'][0], 6)
        self.assertEqual(res4['y'][0][1], 160)
        self.assertEqual(res5['z'], 5)        

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'rtopy.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
