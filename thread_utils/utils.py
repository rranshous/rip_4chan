from Queue import Queue, Empty, Full
from threading import Thread

def thread_out_work(args,f,thread_percentage=.26,fake_it=False):
    results = []
    if fake_it:
        for arg in args:
            results.append(f(*arg))
    else:
        work_queue = Queue()
        result_queue = Queue()
        threads = []
        map(work_queue.put_nowait,args)
        for i in xrange(len(args)*thread_percentage):
            threads.append(thread_out_function(f,work_queue,result_queue))
            threads[-1].start()
        for thread in threads:
            thread.join()
        results = []
        try:
            while True:
                results.append(result_queue.get_nowait())
        except Empty:
            pass
    return results

def thread_out_function(f,in_queue,out_queue):
    def threaded(f,in_queue,out_queue):
        while not in_queue.empty() or out_queue.empty():
            try:
                args = in_queue.get(True,2)
                r = f(*args)
                out_queue.put(r,True)
            except Empty, ex:
                print 'empty'
        return True

    return Thread(target=threaded,kwargs={'f': f,
                                          'in_queue':in_queue,
                                          'out_queue':out_queue})


## idea:
# stage which actors are part of

def MailSorter(object):
    def __init__(self,to_sort_queue):
        # key is address, value: mail queue
        self.mailbox_queues = {}
        # this is the queue new mail comes in to
        self.to_sort_queue = {}

    def get_box(self,address):
        # create the queues if it's the first time we're seeing this
        if not address in self.mailbox_queues:
            self.mailbox_queues[address] = Queue()
        return self.mailbox_queues.get(address)


def Stage(Thread):
    def __init__(self,actor,address_template='%(id)s@local'):
        # dict w/ key as addresses
        self.mailboxes = {}
        # we must start with an actor
        self.seed_actor = actor
        # dict w/ keys as addresses
        self.actors = {}
        # we are going to use sequential ints as
        # the id part of the address
        self.next_id = 1

    def run(self):
        if not self.actors:
            raise Exception('Must have actors to run')
        # we are going to keep our a

class EmptyMailbox(Exception):
    pass

def Actor(Thread):
    BREED = None
    ADDRESS_TEMPLATE = '%(random)s@local'
    def __init__(self,mail_in,mail_out,keep_going):
        self.address = self.ADDRESS_TEMPLATE % self.get_random_string()
        self.keep_going = keep_going # in this case a threading event
        self.mail_in = mail_in
        self.mail_out = mail_out
        self.associates = {}
        # should we print our msg ?
        self.print_out = True
        super(Actor,self).__init__()

    def add_associate(self,address,breed):
        self.associates.setdefault(breed,set).add(address)

    def add_associate_from_msg(self,msg):
        self.add_associate(msg[0][0],msg[0][1])

    def send_msg(self,msg):
        # our msgs are always tuples in tuples
        # ( (address,breed) ,(msg_data,) )
        msg = ((self.address,self.breed),(msg,))
        self.mail_out.put_nowait(msg)

    def get_msg(self,add_sender=True):
        # get our msg from the queue
        try:
            msg = self.mail_in.get_nowait()
        except Empty:
            raise EmptyMailbox

        # based on flag add the sender to our associates
        if add_sender:
            self.add_associate_from_msg(msg)

        return msg

    def run():
        """ take action """
        # we are just going to print every other msg in our mailbox
        while self.keep_going.wait():
            msg = self.get_msg()
            if self.print_out:
                print 'msg'
            self.print_out = not self.print_out
