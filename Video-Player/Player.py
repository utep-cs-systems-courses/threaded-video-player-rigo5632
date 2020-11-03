#! /usr/bin/python3
from threading import Thread, Semaphore, Lock
import cv2, time

class producerConsumerQueue():
    def __init__(self, queueCapacity):
        self.queue = []
        self.fullCount = Semaphore(0)
        self.emptyCount = Semaphore(24)
        self.lock = Lock()
        self.queueCapacity = queueCapacity
        
    def insertFrame(self, frame):
        self.emptyCount.acquire()
        self.lock.acquire()
        self.queue.append(frame)
        self.lock.release()
        self.fullCount.release()
        return
    
    def getFrame(self):
        self.fullCount.acquire()
        self.lock.acquire()
        frame = self.queue.pop(0)
        self.lock.release()
        self.emptyCount.release()
        return frame
    
class ExtractFrames(Thread):
    def __init__(self):  
        Thread.__init__(self)
        self.videoCapture = cv2.VideoCapture('clip.mp4')
        self.totalFrames = int(self.videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.count = 0
        
    def run(self):
        global frameQueue #frame queue
        success, image = self.videoCapture.read()

        while True:
            # if we have an image and our frame queue is not full: add frame
            if success and len(frameQueue.queue) <= frameQueue.queueCapacity: 
                frameQueue.insertFrame(image)

                success, image = self.videoCapture.read() #get next frame from file
                print(f'Reading frame {self.count}')
                self.count += 1

            # we have acquired all frames
            if self.count == self.totalFrames:
                frameQueue.insertFrame(-1)
                break            
        return
            
class ConvertToGrayScale(Thread):
        def __init__(self):
            Thread.__init__(self)
            self.count = 0
            
        def run(self):
            global frameQueue #frame queue
            global grayScaleQueue #grayscale frame queue
            
            while True:
                #if we have frames in our queue and our queue is not full
                if frameQueue.queue and len(grayScaleQueue.queue) <= grayScaleQueue.queueCapacity:
                    frame = frameQueue.getFrame()

                    # if we see end key stop appending gray frames, exit thread
                    if type(frame) == int and frame == -1:
                        grayScaleQueue.insertFrame(-1)
                        break
                    
                    #get frame from queue1, convert it and append it to queue 2
                    print(f'Converting Frame {self.count}')
                    grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    grayScaleQueue.insertFrame(grayscaleFrame)
                    self.count += 1
            return

class ShowMovie(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.delay = 42
        self.count = 0

    def run(self):
        global grayScaleQueue #grayscale queue2

        while True:
            #as long as we have frames in our queue
            if grayScaleQueue.queue:
                frame = grayScaleQueue.getFrame()

                # if we see the end key, exit display thread
                if type(frame) == int and frame == -1:
                    break

                #display frame
                print(f'Displaying Frame {self.count}')
                cv2.imshow('Video', frame)
                self.count += 1

                #exit key
                if cv2.waitKey(42) and 0xFF == ord('q'):
                    break
                    
        #destory video screen
        cv2.destroyAllWindows()
        return

frameQueue = producerConsumerQueue(9)
grayScaleQueue = producerConsumerQueue(9)

extractFrames = ExtractFrames()
extractFrames.start()
convertFrames = ConvertToGrayScale()
convertFrames.start()
displayFrames = ShowMovie()
displayFrames.start()


























