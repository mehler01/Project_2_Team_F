# Planning and Analysis

## Problem Formulation
We were tasked with solving a problem for a static site generator that uses a strict, minimalist typography layout. Given a sequence of $n$ words, we are tasked with rendering them into a simple paragraph. Each line on the webpage has a width of $W$ characters. If a line contains words using $C$ characters, then the aesthetic penalty for leftover whitespace is quantized by $(W-C)\cdot 3$, where $C\leq W$. Note, the last line of the paragraph incurs zero penalty. Our goal is to design an algorithm that breaks the words into lines, and minimalizes the total sum of aesthetic penalties across all lines. 

## Baseline Solution

```
Baseline_solution(words, width):

    Input:
        words # list of words with length n
        width # max num of character for each line

    Output:
        Minimum possible penalty incurred 

    n = len(words)
    W = width

    def recursive(i):

        if i == n: 
            return 0

        best = infinity
        C = 0
        
        for j from i to n-1:
            C += len(words[j]) + 1

            if C -1 > W:
                break

            if j == n - 1:
                cost = 0
            else: 
                cost = (W - C + 1) * 3

            best = min(best, cost + recursive(j+1))

        return best
    
    return recursive(0)
```