import os
import sys
import atexit
import subprocess

class Tasklet_journalctl:
    def __init__(self, swan, journalctl_proc, sjs, message_manager, prevs, wl):
        self.logger = swan.get_logger()
        self.stop_event = swan.get_stop_event()
        self.gs = swan.get_gs()
        self.swan = swan
        self.journalctl_proc = journalctl_proc
        self.sjs = sjs
        self.checkpoint = swan.get_checkpoint()
        self.message_manager = message_manager
        self.prevs = prevs
        self.wl = wl # whitelist
        
        # Register the finisher function for cleanup at exit
        atexit.register(self.finis)

    def finis(self):
        pass

    def process_input(self):
        try:
            while not self.stop_event.is_set() and not self.gs.is_shutdown():
                # Process each line from journalctl -f
                for line in self.journalctl_proc.stdout:
                    # Clean up previous temporary files
                    #clean_temp_files()

                    # should we exit ???
                    if self.gs.is_shutdown():
                        # yes
                        break

                    line = line.strip()

                    # Lets skip audit lines for now
                    is_audit_present = ' audit[' in line
                    if is_audit_present is False:
                        is_audit_present = ' audit: ' in line                
                        if is_audit_present is True:
                            continue
            
                    print(f"mainloop: line = <{line}>")

                    tmp_date = self.sjs.get_datetime(line)
                    if tmp_date is not None:
                        print(f"Updating Checkpoint with date {tmp_date}")
                        self.checkpoint.set(tmp_date)
                        
                    # zDROP check, make a copy of the line before we pass it in
                    if 'zDROP' in line:
                        if self.message_manager is not None:
                            # send a message to Tasker_ZDROP
                            print(f"enqueue line <{line}>")
                            msg = self.message_manager.enqueue(line)
                            time.sleep(.01) # priority scheduling in Python3 - What a joke.
                            continue
                        else:
                            continue # zDROP is true AND message_manager is None
            
                    # Now save on our previous entries list
                    line_copy = line[:]
                    self.prevs.add_entry(line_copy)

                    # combine
                    result = self.prevs.combine()
                    if result is not None:
                        result = result.strip()
                    else:
                        self.logger.fatal("result can't be None")
                        sys.exit(0)

                    self.logger.debug(f"combine_result: {result}")
            
                    # is there an ip address in result ???
                    result_copy = result[:]
                    found_dict, shortened_str = self.sjs.shorten_string(result_copy)

                    # debug
                    self.logger.debug(f"shortened_str = {shortened_str}")

                    # check to see we have an ip address, if no, continue
                    if 'ip_address' in found_dict:
                        ip_address = found_dict['ip_address']
                        # debgging info
                        #logging.debug(f"ip_address found by shorten_string is {ip_address}")
                    else:
                        # debgging info
                        #logging.debug(f"no ip_address found, skipping line")
                        # we are done if there is not ip_address, on to the next line
                        continue

                    if False:
                        # this was taken out here as this belongs in FinalDisposer
                        # get country and bad_dude_status
                        country = None
                        bad_dude_status = "n/a"
                        if ip_address is not None:
                            country = find_country(ip_address)
                            # is this ip address in HashedSet
                            if hs.is_ip_in_set(ip_address) :
                                # yep, a really bad dude
                                bad_dude_status = True
                            else:
                                # nope, but a bad dude anyway
                                bad_dude_status = False

                    #  is ip_address in our whitelist ???
                    ip_address_in_whitelist = None
                    if ip_address is not None:
                        # check that this ip is not in the whitelist
                        if self.wl.is_whitelisted(ip_address) is True:
                            ip_address_in_whitelist = True
                        else:
                            ip_address_in_whitelist = False                    

                    if False:
                        # this was taken out here as this belongs in FinalDisposer
                        # check hazard level from table threat_table in database
                        hazard_level = "unk"
                        tmp_flag, tmp_hazard_level = db.fetch_threat_level(shortened_str)
                        # was the record found in the database ???
                        if tmp_flag is True:
                            # yes
                            hazard_level = tmp_hazard_level
                        else:
                            pass

                    # format message to be displayed
                    formatted_string = (
                        f"Line      : {result if result is not None else 'n/a'}\n"
                        f"Dictionary: {found_dict if found_dict is not None else 'n/a'}\n"
                        f"Shortened : {shortened_str if shortened_str is not None else 'n/a'}\n"
                        f"InWhiteLst: {ip_address_in_whitelist if ip_address_in_whitelist is not None else 'n/a'}"
                    )
                    # and display it
                    print(formatted_string)
                    print("-" * 50)
        
                    if False:
                        # this was taken out here as this belongs in FinalDisposer
                        # if we are debugging,
                        if logger.getEffectiveLevel() <= FLAG_DEBUG :
                            # at this point, we'd want to check with ChatGPT to ascertain the hazard_level level
                            # then add to our threat database
                            db.insert_or_update_threat(shortened_str, 1, hazard_level)

                    # Finally! We can kick off FinalDisposer - TODO

        except Exception as e:
            # Catch the exception and display the error
            self.loggger.error(f"An error occurred: {e}")
        finally:
            return False # We should never return
        
# run this tasklet
def run_tasklet_journalctl(data, **kwargs):
    # get args from kwargs
    swan = kwargs.get('swan', None)
    conn = kwargs.get('conn', None)
    message_manager = kwargs.get('message_manager', None)
    logger = swan.get_logger()
    
    stop_event = swan.get_stop_event()

    # If we have a valid checkpoint, we must start watching journalctl at that time
    since_time = swan.get_checkpoint().get()
    if since_time is None:
        command = ['journalctl', '-f']
    else:
        command = ['journalctl', '-f', f'--since={since_time}']
    # Start journalctl
    journalctl_proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # and our ShortenJournalString
    sjs = ShortenJournalString.ShortenJournalString()
    # use PreviousJournalctl
    prevs = PreviousJournalctl()
    # our whitelist
    wl = WhiteList.WhiteList()
    
    # create our class
    tj = Tasklet_journalctl(swan, journalctl_proc, sjs, message_manager, prevs, wl)
    
    if False:
        work_controller = kwargs.get('work_controller', None)
        message_manager = kwargs.get('message_manager', None)
        tasklet_zdrop = Tasklet_ZDrop(work_controller, message_manager, conn)
        while not stop_event:
            message_unit = message_manager.dequeue()
            if message_unit is None: #shutdown condition
                print("Shutting down Tasklet_ZDrop")
                break
            tasklet_zdrop.is_zdrop(message_unit.get_message_string())

    # do the deed
    status = tj.process_input()

    # report that we are done
    logger.info(f"run_tasklet_journalctl returns with status = {status}")
        
if __name__ == "__main__":

    project_root = os.getenv("FAIL3BAN_PROJECT_ROOT")
    # Add the constructed path to sys.path only if it's not already in sys.path
    lib_path = os.path.join(project_root, 'lib')
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)
        print(f"Prepending {lib_path} to sys.path")

    from Swan import Swan
    # get ShortenJournalString
    import ShortenJournalString
    # get prevs
    from PreviousJournalctl import PreviousJournalctl
    # get whitelist
    import WhiteList

    swan = Swan()
    stop_event = swan.get_stop_event()
    logger = swan.get_logger()

    data = 'Tasklet_journalctl'
    kwargs={'stop_event'               : stop_event,
            'logger'                   : logger,
            'swan'                     : swan
            }
    run_tasklet_journalctl(data, **kwargs)

    logger.info("Tasklet done")
