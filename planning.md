# Planning and Analysis

## Problem Formulation
We were tasked with solving a problem for a static site generator that uses a strict, minimalist typography layout. Given a sequence of $n$ words, we are tasked with rendering them into a simple paragraph. Each line on the webpage has a width of $W$ characters. If a line contains words using $C$ characters, then the aesthetic penalty for leftover whitespace is quantized by $(W-C)\cdot 3$, where $C\leq W$. Note, the last line of the paragraph incurs zero penalty. Our goal is to design an algorithm that breaks the words into lines, and minimalizes the total sum of aesthetic penalties across all lines. 

## Baseline Solution
To establish a baseline algorithm, we used an iterative approach. This approach iterates through each word, adding them to the current paragraph line until the width limit is met. It accounts for the space after each word, but makes sure to remove the space after the last word when accounting for the penalty. Additionally, once the last word is reached, no penalty is added.

In terms of the recursive approach, the algorithm constructs a line of words until the width limit is met, it then calculate the penalty cost of the given line, and calls the recursive algorithm. The recursive algorithm then goes through the same process for all the remaining words, and tries all possible line options until the minimal penalty is reached.
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

        # if there are no words remaining, no penalty is incurred
        # and the algorithm stops

        best = infinity
        C = 0

        # set initial conditions
        
        for j from i to n-1:
            C += len(words[j]) + 1

            if C -1 > W:
                break

            # break so that line width isn't exceeded 

            if j == n - 1:
                cost = 0

            # no penalty for last line 

            else: 
                cost = (W - C + 1) * 3

            best = min(best, cost + recursive(j+1))

            # after a line is completed, the recursive algorithm # is called to produce the minimal penalty with the # remaining words

        return best
    
    return recursive(0)
```

## Optimized Solution
We will use dynamic programming to improve our recursive baseline. We add a table called memo to save answers we have already calculated. Before solving the remaining words, we check whether the answer is saved. If it is, we reuse it instead of repeating the same calculations.
```
Optimized_solution(words, width):
    n = len(words)
    W = width
    memo = empty table

    def recursive(i):
        if i == n:
            return 0

        if i is in memo:
            return memo[i]

        best = infinity
        C = 0

        for j from i to n-1:
            C += len(words[j]) + 1

            if C - 1 > W:
                break

            if j == n - 1:
                cost = 0
            else:
                cost = (W - C + 1)^3

            best = min(best, cost + recursive(j + 1))

        memo[i] = best
        return best

    return recursive(0)
```
## Time Complexity
Our baseline solution using the purely recursive approach operates inefficiently compared to our optimized solution. The baseline algorithm operates with a $\mathcal{O}(2^n)$ time complexity. This is because each call tries every line that fits, then recurses on the remaining words, so the same remaining words get recomputed over and over. In the worst case, every word fits on one line, so each word either ends a line or doesn’t, doubling the number of calls for each extra word. 

The optimized algorithm has a worst-case running time of $\Theta(n^2)$. Each starting position is solved only once, and the maximum number of checks is:

$n+(n-1)+\cdots+1=\frac{n(n+1)}{2}.$

Each check takes constant time, assuming word lengths and arithmetic take constant time. The algorithm uses $O(n)$ extra space for saved answers and recursive calls.