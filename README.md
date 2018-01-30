# pixel-matcher
Multi file image differ, with the intent of producing art rather than being technically useful. I'll write up how the algorithm works later.

Here's an example. It's the first good output I've gotten.

![First decent output](https://github.com/okiyama/pixel-matcher/blob/master/gifs/animation1511647289.gif)

It is corrupting this image:

![Parent image](https://github.com/okiyama/pixel-matcher/blob/master/parents/abstract-colorsdd5a-turquoise-sq.jpg)

TODO:  
 * Rather than all or nothing on each pixel, have the pixel show the relative frequency through it's alpha value.   
 * Average the pixel values or choose median pixel  
 * Automatically resize child images to match parent    
 * Use HSV values instead, could give interesting effects from the color wheel    
 * Performance improvements, it's still really slow    
 * For GIF creation, track created files and delete after the run is done. Safer than just deleting the output folder.    
 * Look into matrix-izing distance calculations. I think I could just hand in the parent and child matrices and get out the diff map. Not a huge deal though, most of time is spent comparing diff map to current pixel values.    

DONE:
 * Paralellization would work well. Would need to break up into discrete processes that can be called with command line parameters. This honestly would improve the quality of the program though    
 * Generate gifs of the output with different thresholds    
 * Let closer pixel trump further   
 * Save to .gifv rather than .gif    