import keyboard as kb
import numpy as np
from scipy import stats
from termcolor import colored
import time

PHRASE = "somebody"
LOGGED_IN = 0


choice = -1

class MathAndEverything():
    def expectation(self, a):
        n=len(a)
        prb = 1 / n
        sum = 0
        for i in range(0, n):
            sum += (a[i] * prb)
        return float(sum)

    def variance(self, a, m=0):
        n = len(a)
        mean = sum(a) / n
        if m!=0:
            mean = m
        deviations = [(x - mean) ** 2 for x in a]
        variance = sum(deviations) / (n-1)
        return variance

    def stdeviation(self, a):
        return a**0.5

    def stcoef(self, y, M, S):
        return float(abs((y-M)/S))

    def tabstcoef(self, n, alpha):
        return abs(stats.t.ppf(alpha/2, n))

    def authstcoef(self, m1, m2, s1, s2, a):
        n = len(a)
        s = (((s1**2+s2**2)*(n-1))/(2*n-1))**0.5
        tp = abs(m1-m2)/(s*((2/n)**0.5))
        return tp

    def fishcoef(self, s1, s2, n):
        if s1>s2:
            smax, smin = s1, s2
        else:
            smax, smin = s2, s1
        fp = float(smax/smin)
        ft = stats.f.isf(0.05, n-1, n-1)
        return fp<ft



class InputOutput():
    borders = 'cyan'
    outtext = 'yellow'
    intext = 'white'

    def filewr(self, username, interv, exp, var, n):
        with open('data.txt', 'a') as f:
            f.write(username+'#'+','.join([str(i) for i in interv])+'#'+str(exp)+'#'+str(var)+'#'+str(n)+'\n')

    def getRecords(self, username):
        records = self.fileread()
        records = [str(i)[2:-1].split('#') for i in records]
        res = []
        for record in records:
            if username == record[0]:
                res.append(record)
        return res

    def outColorMess(self, message):
        print(colored("#", self.borders)*50)
        print(colored("#", self.borders)+" "*9+colored(message, self.intext)+" "*(50-len(message)-9-2)+colored("#", self.borders))
        print(colored("#", self.borders)*50)
        return

    def formatMiddle(self, message):
        return colored("#", self.borders)+" "*9+colored(message, self.intext)+" "*(50-len(message)-9-2)+colored("#", self.borders)

    def menu(self, option):
        print(colored("#", self.borders)*50)
        if option==0:
            print(self.formatMiddle("Choose the operation:"))
            print(self.formatMiddle("0. exit"))
            print(self.formatMiddle("1. sign up"))
            print(self.formatMiddle("2. log in"))
        print(colored("#", self.borders)*50)

    def fileread(self):
        with open('data.txt', 'rb') as f:
            return f.read().split(b'\n')[:-1]



class Calc():
    m = MathAndEverything()
    io = InputOutput()
    intervals = []

    def on_action(self,event):
        self.intervals.append(time.time())

    def getIntervals(self):
        self.intervals = []
        res = []
        for i in set(PHRASE):
            kb.on_press_key(i, self.on_action)
            kb.on_release_key(i, self.on_action)
        a = input("> ")
        if a!=PHRASE:
            kb.unhook_all()
            return []
        kb.unhook_all()
        res = self.intervals[1:-1]
        return [res[2*i+1]-res[2*i] for i in range(len(res)//2)]

    def exclusion(self, a):
        if len(a)==0:
            return False, []
        exp = []
        var = []
        stdev = []
        stcoefs = []
        tstcoef = self.m.tabstcoef(len(a)-2, 0.05)
        for i in range(len(a)):
            exp.append(self.m.expectation(a[:i]+a[i+1:]))
            var.append(self.m.variance(a[:i]+a[i+1:], exp[i]))
            stdev.append(self.m.stdeviation(var[i]))
            stcoefs.append(self.m.stcoef(a[i], exp[i], stdev[i]))
            if stcoefs[i]>tstcoef:
                return self.exclusion(a[:i]+a[i+1:])
                #return False, []
        return True, a

class Pr():
    m = MathAndEverything()
    c = Calc()
    io = InputOutput()

    def receive(self):
        interv = []
        while len(interv)!=len(PHRASE)-1:
            self.io.outColorMess("Type: "+PHRASE)
            interv = self.c.getIntervals()
        exc, interv = self.c.exclusion(interv)
        if exc:
            return interv
        else:
            return self.receive()

    def runOperation(self,choice):
        if choice == 0:
            self.io.outColorMess("Thank you. Good bye!")
        elif choice == 1:

            self.io.outColorMess("Type your username:")
            username = input("> ")

            records = io.getRecords(username)
            if records!=[]:
                self.io.outColorMess("The username is taken")
                return self.runOperation(1)

            for j in range(5):
                interv = self.receive()

                exp = self.m.expectation(interv)
                var = self.m.variance(interv)

                self.io.filewr(username, interv, exp, var, j)
            self.io.outColorMess("New user registered.")
        elif choice == 2:
            self.io.outColorMess("Type your username:")
            username = input("> ")

            records = io.getRecords(username)
            if records==[]:
                self.io.outColorMess("Such username does not exist")
                return

            interv = self.receive()

            exp = self.m.expectation(interv)
            var = self.m.variance(interv)
            tt = self.m.tabstcoef(len(interv)-1, 1-0.9)

            k=0
            for record in records:
                tp = self.m.authstcoef(exp, float(record[2]), var, float(record[3]), interv)
                if self.m.fishcoef(var, float(record[3]), len(interv)):
                    if tp>tt:
                        k+=1
            if k/5>0.5:
                self.io.outColorMess("You are logged in!")
            else:
                self.io.outColorMess("You shall not pass!")

        else:
            self.io.outColorMess("Wrong operation")


io = InputOutput()
p = Pr()

io.outColorMess("BIOMETRIC AUTHENTICATION")

while choice!=0:
    io.menu(0)
    try:
        choice = int(input("> "))
        p.runOperation(choice)
    except:
        choice = -1
