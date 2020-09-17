'''
*****
...........................c..
......cc..............cc...c..
.....c..c............c..c..c..
.....c.ccccccc......ccc.c..c..
.....c..c.....t.....c.c.c..c..
.....c.c.c.....h.....c..c..c..
.c...c.ccc......ccccccc.c..c..
c.c..c..c............c..c..c..
c.c...cc..............cc...c..
c.c........................c..
c.c........................c..
c.c.......thc..............c..
c.c......c...t............th..
t.c.......cchhh...............
.h...........c................
..ccccccc...c.cccccccccccccccc
.........c.c..................
..cccc..ccc...cccccccccccccccc
.h....c..c.c.c................
t.c...c..c.c.c................
c.c...c..c.c.c................
c.c....cc...c.................
c.c.......chhh................
c.c......t..t......cccc.......
c.c.....h..c......c....c......
c.t......cc......c..ccc.......
.h..............c..c..........
.........h.ccccc....cccccccccc
........t.c...................
.........c.ccccccccccccccccccc
*****
'''

##########################################################################################################################################

class Grid :

    _none,_copper,_head,_tail = 0,1,2,3

    def __init__(self,size=None):
        if not self._read( size ):
            try    : self._create( size )
            except : self._create( (30,30) )

    def _create(self,size):
        self.x      = size[0]
        self.y      = size[1]
        self.heads  = []
        self.tails  = []
        self.change = set([])
        self.next   = [0]*self.x*self.y
        self.grid   = [self._none]*self.x*self.y
        for y in xrange( self.y ):
            for x in xrange( self.x ):
                next,i = [],x+y*self.x
                for (xx,yy) in ((-1,-1),(-1,0),(-1,1),(0,1),(0,-1),(1,-1),(1,0),(1,1)):
                    if 0 <= x+xx < self.x and 0 <= y+yy < self.y :
                        next += [(x+xx)+(y+yy)*self.x]
                    self.next[i] = tuple( next )

    def _read (self,filename):
        try:
            try    : data = open( filename ).read()
            except : data = filename
            if '*****' in data :
                data = data.split('*****')[1]
            data = filter( None,data.split('\n'))
            x,y  = len( data[0] ),len( data )
            data = ''.join( data )
            self._create((x,y))
            for i,c in enumerate( data ):
                self._set( i,'.cht'.index( c ))
            return True
        except:
            return False

    def size (self):
        return (self.x,self.y)

    def step (self):
        candidates = {}
        for pos in self.heads :
            for n in self.next[pos] :
                if self.grid[n] == self._copper:
                    candidates[n] = candidates.setdefault( n,0 ) + 1
        for pos in self.tails :
            self.grid[pos] = self._copper
            self.change.add( pos )
        self.tails = []
        for pos in self.heads :
            self.grid[pos] = self._tail
            self.tails  += [pos]
            self.change.add( pos )
        self.heads = []
        for pos,nb in candidates.iteritems() :
            if nb in (1,2):
                self.grid[pos] = self._head
                self.heads += [pos]
                self.change.add( pos )
        return self

    def _set (self,pos,state):
        if self.grid[pos] != state :
            if   self.grid[pos] == self._head : self.heads.remove( pos )
            elif self.grid[pos] == self._tail : self.tails.remove( pos )
            if   state          == self._head : self.heads.append( pos )
            elif state          == self._tail : self.tails.append( pos )
            self.grid[pos] = state
            self.change.add( pos )

    def set (self,pos,state):
        self._set( pos[0]+pos[1]*self.x,state )

    def get (self,pos ):
        return self.grid[pos[0]+pos[1]*self.x]

    def inc (self,pos,inc):
        pos = pos[0]+pos[1]*self.x
        self._set( pos,(self.grid[pos]+inc)%4 )
        return self.grid[pos]

    def iter (self,only_changed=False):
        if only_changed :
            for i in self.change:
                x,y = i % self.x , i / self.x
                yield x,y,i,self.grid[i]
            self.change = set([])
        else:
            for y in xrange( self.y ):
                for x in xrange( self.x ):
                    i = x+y*self.x
                    yield x,y,i,self.grid[i]

    def changed (self):
        res,self.change = self.change,False
        return res

##########################################################################################################################################

class Random :
    def __init__ ( self,*param ):
        if len( param ) == 1 :
            param = param[0]
        try :
            sx,sy = int( param[0] ),int( param[1] )
            map   = '\n'.join( 'c'*sx for i in xrange( sy ))
            self.grid  = Grid( 'h' + map[1:] )
            self.pos   = (sx/2,sy/2)
        except:
            try:
                self.pos  = param[1]
                self.grid = Grid( param[0] )
            except:
                raise Exception('Random( (sizex,sizey) ) or Random( "..cc\ncccc",(1,2) )')
    def __call__ (self):
        if 1 :
            self.grid.step()
            return int( self.grid.get( self.pos ) == 1 )
        num = lambda : int( self.grid.step().get( self.pos ) == 1 )
        x = sum( num() << i for i in xrange( 2 ))
        return x/2


def TestRandom ( random,nbbit ):
    stat = [0]*(1<<nbbit)
    while 1 :
        print '-'*100
        x = sum( random() << i for i in xrange( nbbit ))
        stat[x] += 1
        for i in xrange( 1 << nbbit ):
            print '%02x:%-3d'%( i,stat[i] ),
            if i % 16 == 15 : print

if 0 :
    TestRandom( Random( 17,13 ),2 )

##########################################################################################################################################

def Dialog ( title,grid,pixsize ):
    import Tkinter

    def run ( init ):
        if init :
            self.runing = not self.runing
        if self.runing :
            grid.step()
            redraw()
            self.root.after(10,run,False)

    def update ():
        self.runing = False
        grid.step()
        redraw()

    def clic ( x,y,b,p ):
        if p :
            if self.pressed :
                grid.set( (x,y),self.value )
            else:
                self.value = grid.inc( (x,y),(1,-1)[b])
            redraw()
        self.pressed = p

    def moved ( x,y ):
        if self.pressed :
            grid.set( (x,y),self.value )
            redraw()

    def draw ():
        for x,y,index,state in grid.iter( False ):
             self.box[index] = self.can.create_rectangle( x*pixsize,y*pixsize,(x+1)*pixsize,(y+1)*pixsize,fill=self.colors[state],width=int(pixsize > 4) )

    def redraw ():
        for x,y,index,state in grid.iter( True ):
            self.can.itemconfig( self.box[index],fill=self.colors[state] )

    class Context : pass
    self = Context()
    self.colors     = ('black','brown','lightblue','white')
    self.pressed    = False
    self.value      = -1
    self.runing     = False
    self.nx,self.ny = grid.size()
    self.box        = [0]*(self.nx*self.ny)
    self.root       = Tkinter.Tk()
    self.root.title( title )
    self.root.geometry('%dx%d+%d+%d' % (self.nx*pixsize,self.ny*pixsize,20,30 ))
    self.root.bind('<Escape>'         ,lambda e : self.root.quit())
    self.root.bind('<Button-1>'       ,lambda e : clic( e.x/pixsize,e.y/pixsize,0,True ))
    self.root.bind('<Button-3>'       ,lambda e : clic( e.x/pixsize,e.y/pixsize,1,True ))
    self.root.bind('<ButtonRelease-1>',lambda e : clic( e.x/pixsize,e.y/pixsize,0,False ))
    self.root.bind('<ButtonRelease-3>',lambda e : clic( e.x/pixsize,e.y/pixsize,1,False ))
    self.root.bind('<Motion>'         ,lambda e : moved( e.x/pixsize,e.y/pixsize ))
    self.root.bind('<space>'          ,lambda e : update())
    self.root.bind('<Return>'         ,lambda e : run( True ))
    self.can = Tkinter.Canvas( self.root,width = self.nx*pixsize,height = self.ny*pixsize )
    self.can.grid()
    draw()
    self.root.mainloop()
    self.root.destroy()

##########################################################################################################################################

import sys
Dialog( 'WireWorld by HF',Grid( sys.argv[0] ),15 )
