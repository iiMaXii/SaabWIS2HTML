#!/usr/bin/env python3

import subprocess
import time
import concurrent.futures
import threading
import os
import sys
import win32api
import win32com.client
import pythoncom
import win32process
import pywintypes

TOTAL_ACTIVE_WORKERS = 4
JOBS_PER_WORKER = 20

#cad_converter_x = 'C:\\Program Files (x86)\\Coolutils\\TotalCADConverterX\\CADConverterX.exe'


def cad_converterx_is_installed():
    try:
        pythoncom.CoInitialize()
        client = win32com.client.dynamic.Dispatch('CADConverter.CADConverterX')
        pythoncom.CoUninitialize()
    except pywintypes.com_error as e:
        # Error: The specified module could not be found. (-2147024770)
        # print('Error: {} ({})'.format(win32api.FormatMessage(e.hresult).strip(), e.hresult))
        return False

    return True


class Worker:
    def __init__(self, output_path):
        self.output_path = output_path
        self.input_files = []
        self.process = None

    def convert(self, input_files):
        self.input_files = input_files
        cmd = ['python', 'coolutils_worker.py', '--output-path', self.output_path]
        cmd.extend(input_files)

        print(cmd)

        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def is_alive(self):
        return self.process and self.process.poll() != 0

    def was_successful(self):
        return not self.process or self.process.returncode == 0

input_path = 'C:\\Users\\iiMaXii\\PycharmProjects\\SaabWIS2HTML\\static\\data\\images\\gcm\\'
output_file = 'C:\\Users\\iiMaXii\\Desktop\\out\\'

if __name__ == '__main__':
    image_list = [os.path.join(input_path, f) for f in os.listdir(input_path)]

    workers = [Worker(output_file) for _ in range(TOTAL_ACTIVE_WORKERS)]

    successful = 0
    total = len(image_list)

    time_start = time.time()
    working = True
    while working:
        for w in workers:
            if not w.is_alive():
                if w.was_successful():
                    input_files = image_list[:JOBS_PER_WORKER]
                    image_list = image_list[JOBS_PER_WORKER:]

                    successful += JOBS_PER_WORKER

                    complete_percentage = successful / total
                    print('percentage={0:.2f}%'.format(complete_percentage))
                    if successful > 5 * JOBS_PER_WORKER:
                        time_difference = time.time() - time_start
                        #etc = (1 - complete_percentage) * time_difference / complete_percentage
                        etc = time_difference/complete_percentage - time_difference
                        print('etc={0:.2f}'.format(etc))

                    w.convert(input_files)
                else:
                    print('Error: worker could not process images')
                    print(w.input_files)
                    sys.exit()



    """
    input_path = 'C:\\Users\\iiMaXii\\PycharmProjects\\SaabWIS2HTML\\static\\data\\images\\gcm\\'
    output_file = 'C:\\Users\\iiMaXii\\Desktop\\out\\'
    log_path = 'C:\\Users\\iiMaXii\\Desktop\\'
    
    image_list = [os.path.join(input_path, f) for f in os.listdir(input_path)]
    image_list = image_list[100:]
    try:
        pythoncom.CoInitialize()
        client = win32com.client.dynamic.Dispatch('CADConverter.CADConverterX')
        pythoncom.CoUninitialize()
    except pywintypes.com_error as e:
        # Error: The specified module could not be found. (-2147024770)
        print('Error: {} ({})'.format(win32api.FormatMessage(e.hresult).strip(), e.hresult))
        sys.exit()
    
    
    class ConversionStatistics:
        def __init__(self, total=0):
            self.successful = 0
            self.errors = 0
            self.total = total
    
            self.failed = []
    
    
    class ConverterWorker(threading.Thread):
        def __init__(self, working_queue: list, conversion_statistics: ConversionStatistics, destination_path, log_file):
            super(ConverterWorker, self).__init__()
            self.working_queue = working_queue
            self.conversion_statistics = conversion_statistics
            self.destination_path = destination_path
            self.log_file = log_file
    
        def run(self):
            pythoncom.CoInitialize()
            client = win32com.client.Dispatch('CADConverter.CADConverterX')
            pythoncom.CoUninitialize()
            while self.working_queue:
    
                #client = win32com.client.Dispatch('CADConverter.CADConverterX')
    
                input_file = self.working_queue.pop()
                file_name, _ = os.path.splitext(os.path.basename(input_file))
                output_file = os.path.join(self.destination_path, file_name + '.png')
    
                #print('Converting {} -> {}'.format(input_file, output_file))
    
                pythoncom.CoInitialize()
                try:
                    pythoncom.CoInitialize()
                    client.convert(input_file, output_file, '-c PNG -log {}'.format(self.log_file))
                    self.conversion_statistics.successful += 1
                except pywintypes.com_error as e:
                    print('Error:', win32api.FormatMessage(e.hresult).strip())
                    print('Error:', win32api.FormatMessage(e.excepinfo[5]).strip())
    
                    self.conversion_statistics.errors += 1
                    self.conversion_statistics.failed.append(input_file)
                    return
                pythoncom.CoUninitialize()
                #del client
                #gc.collect()
                #else:
                #    if not os.path.isfile(output_file):
                #        self.conversion_statistics.errors += 1
    
    # Set-up converter
    #pythoncom.CoInitialize()
    #cad_instance = win32com.client.Dispatch('CADConverter.CADConverterX')
    #cad_id = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, cad_instance)
    
    
    stats = ConversionStatistics(len(image_list))
    threads = []
    for i in range(TOTAL_WORKERS):
        threads.append(ConverterWorker(image_list, stats, output_file, os.path.join(log_path, 'CADConverterX{}.log'.format(i))))
    
    for t in threads:
        t.start()
    
    # Wait for all threads to finnish
    #for t in threads:
    #   t.join()
    
    start_time = time.time()
    while any(t.isAlive() for t in threads):
    
        print('{} of {}'.format(stats.successful, stats.total))
        if stats.errors:
            print('Errors: {}'.format(stats.errors))
    
        print('interface count: ',pythoncom._GetInterfaceCount())
    
        time_difference = time.time() - start_time
        complete_percentage = (stats.successful + stats.errors) / stats.total
        print('{0:.2f}%'.format(100*complete_percentage))
        if time_difference > 5:
            etc = (1-complete_percentage) * time_difference / complete_percentage
            print('Time left: {0:.2f}'.format(etc))
    
        time.sleep(1)
    
    print()
    print('{} of {}'.format(stats.successful, stats.total))
    print('STOP')
    print()
    print('refcount=', pythoncom._GetInterfaceCount())
    
    """

    # Remove empty log files
    #for i in range(TOTAL_WORKERS):
    #    log_file = os.path.join(log_path, 'CADConverterX{}.log'.format(i))
    #    if os.path.exists(log_file) and os.path.getsize(log_file) == 0:
    #        os.remove(log_file)

    """
    def convert_cad_image(input_file):
        global complete_count
    
        if subprocess.call([cad_converter_x, input_file, output_file, '-c', 'PNG']) != 0:
            image_errors.append(input_file)
    
        complete_count += 1
    
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=TOTAL_WORKERS)
    future = executor.map(convert_cad_image, image_list)
    
    
    while 1:
        print(complete_count, 'of', len(image_list))
        print('errors:', image_errors)
        time.sleep(2)
    """
    """pool = ThreadPool(4)
    results = pool.map(image_converter_worker, image_queue)
    
    results = []
    for item in my_array:
        results.append(my_function(item))
    
    workers = []"""

    """
    for i in range(TOTAL_WORKERS):
        t = threading.Thread(target=image_converter_worker, args=(image_queue,))
        workers.append(t)
        t.daemon = True
        t.start()
    """
