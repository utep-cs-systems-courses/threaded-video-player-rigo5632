# Producer and Consumer lab

For this lab I had to create multiple threads that will be able to extract
frames from a video file, convert them in grayscale frames and finally display
them into a video player. These threads will have access to queues (locks are
necessary) that will store and pop frames from these queues.



## How to Run:

```bash

python3 Player.py

```

or

```bash

./Player.py

```

## How it Works:



### Thread 1

* Extract frames from mp4 file

* Append frames to queue 1



### Thread 2

* Get queue1 and pop frames from it

* Convert popped frames to grayscale and append it to queue 2



### Thread 3

* Get queue2 and pop frames from it

* Display popped frames 
