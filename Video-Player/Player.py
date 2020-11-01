#! /usr/bin/python3
from threading import Thread, Semaphore
import cv2, time

semaphore = Semaphore(2)
frameQueue = []
grayScaleQueue = []

class ExtractFrames(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.videoCapture = cv2.VideoCapture('clip.mp4')
        self.totalFrames = int(self.videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.queueCapacity = 50
        self.count = 0
        
    def run(self):
        global frameQueue #frame queue
        global semaphore #lock
        success, image = self.videoCapture.read()

        while True:
            # if we have an image and our frame queue is not full: add frame
            if success and len(frameQueue) <= self.queueCapacity:
                semaphore.acquire() #lock
                frameQueue.append(image)
                semaphore.release() #lock

                success, image = self.videoCapture.read() #get next frame from file
                print(f'Reading frame {self.count}')
                self.count += 1

            # we have acquired all frames
            if self.count == self.totalFrames:
                semaphore.acquire()
                frameQueue.append(-1) #append end key
                semaphore.release()
                break            
        return
            
class ConvertToGrayScale(Thread):
        def __init__(self):
            Thread.__init__(self)
            self.queueCapacity = 50
            self.count = 0
            
        def run(self):
            global frameQueue #frame queue
            global grayScaleFrame #grayscale frame queue
            global semaphore #lock
            
            while True:
                #if we have frames in our queue and our queue is not full
                if len(frameQueue) >= 1 and len(grayScaleQueue) <= self.queueCapacity:
                    semaphore.acquire()
                    frame = frameQueue.pop(0) #pop frame from queue1
                    semaphore.release()

                    # if we see end key stop appending gray frames, exit thread
                    if type(frame) == int and frame == -1:
                        semaphore.acquire()
                        grayScaleQueue.append(-1)
                        semaphore.release()
                        break
                    
                    #get frame from queue1, convert it and append it to queue 2
                    print(f'Converting Frame {self.count}')
                    grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    semaphore.acquire()
                    grayScaleQueue.append(grayscaleFrame)
                    semaphore.release()
                    self.count += 1
                else:
                    time.sleep(0.10) # sleep if we don't need to do work
            return

class ShowMovie(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.delay = 42
        self.count = 0

    def run(self):
        global grayScaleQueue #grayscale queue2
        global semaphore #lock

        while True:
            #as long as we have frames in our queue
            if len(grayScaleQueue) >= 1:
                semaphore.acquire()
                frame = grayScaleQueue.pop(0) #pop frame from queue2
                semaphore.release()

                # if we see the end key, exit display thread
                if type(frame) == int and frame == -1:
                    break

                #display frame
                print(f'Displaying Frame {self.count}')
                cv2.imshow('Video', frame)
                self.count += 1

                #exit key
                if cv2.waitKey(self.delay) and 0xFF == ord('q'):
                    break
            else:
                time.sleep(0.10) #sleep if we don't need to do work
                    
        #destory video screen
        cv2.destroyAllWindows()
        return

extractFrames = ExtractFrames()
extractFrames.start()
convertFrames = ConvertToGrayScale()
convertFrames.start()
displayFrames = ShowMovie()
displayFrames.start()




























