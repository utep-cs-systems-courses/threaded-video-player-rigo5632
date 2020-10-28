#! /usr/bin/python3
from threading import Thread, Semaphore
import cv2, time

semaphore = Semaphore(2)
queue1 = []
queue2 = []

class ExtractFrames(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.videoCapture = cv2.VideoCapture('clip.mp4')
        self.totalFrames = int(self.videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.queueCapacity = 50
        self.count = 0
        
    def run(self):
        global queue1 #frame queue
        global semaphore #lock
        success, image = self.videoCapture.read()

        while True:
            # if we have an image and our frame queue is not full: add frame
            if success and len(queue1) <= self.queueCapacity:
                semaphore.acquire() #lock
                queue1.append(image)
                semaphore.release() #lock

                success, image = self.videoCapture.read() #get next frame from file
                print(f'Reading frame {self.count}')
                self.count += 1

            # we have acquired all frames
            if self.count == self.totalFrames:
                semaphore.acquire()
                queue1.append(-1) #append end key
                semaphore.release()
                break
        return
            
class ConvertToGrayScale(Thread):
        def __init__(self):
            Thread.__init__(self)
            self.queueCapacity = 50
            self.count = 0
            
        def run(self):
            global queue1 #frame queue
            global queue2 #grayscale frame queue
            global semaphore #lock
            
            while True:
                #if we have frames in our queue and our queue is not full
                if queue1 and len(queue2) <= self.queueCapacity:
                    semaphore.acquire()
                    frame = queue1.pop(0) #pop frame from queue1
                    semaphore.release()

                    # if we see end key stop appending gray frames, exit thread
                    if type(frame) == int and frame == -1:
                        semaphore.acquire()
                        queue2.append(-1)
                        semaphore.release()
                        break
                    
                    #get frame from queue1, convert it and append it to queue 2
                    print(f'Converting Frame {self.count}')
                    grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    semaphore.acquire()
                    queue2.append(grayscaleFrame)
                    semaphore.release()
                    self.count += 1
            return

class ShowMovie(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.delay = 42
        self.count = 0

    def run(self):
        global queue2 #grayscale queue2
        global semaphore #lock

        while True:
            #as long as we have frames in our queue
            if queue2:
                semaphore.acquire()
                frame = queue2.pop(0) #pop frame from queue2
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
        #destory video screen
        cv2.destroyAllWindows()
        return

extractFrames = ExtractFrames()
extractFrames.start()
convertFrames = ConvertToGrayScale()
convertFrames.start()
displayFrames = ShowMovie()
displayFrames.start()






























