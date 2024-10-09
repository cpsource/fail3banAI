
class Tasklet_journalctl:
    def __init__(self, swan):
        self.logger = swan.get_logger()
        self.stop_event = swan.get_stop_event()

# wait_and_process
def wait_and_process(data, **kwargs):
    # get args from kwargs
    swan = kwargs.get('swan', None)
    conn = kwargs.get('conn', None)

    stop_event = swan.get_stop_event()

    tj = Tasklet_hournalctl(swan)
    
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

if __name__ == "__main__":
    
# Our Main Loop - TODO: belongs as a Tasklet
try:
    while not stop_event.is_set() and not gs.is_shutdown():
        # Process each line from journalctl -f
        for line in journalctl_proc.stdout:
            # Clean up previous temporary files
            #clean_temp_files()

            # should we exit ???
            if gs.is_shutdown():
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

            tmp_date = sjs.get_datetime(line)
            if tmp_date is not None:
                print(f"Updating Checkpoint with date {tmp_date}")
                checkpoint.set(tmp_date)

            if tst is True:
                line = "Sep 25 14:53:52 ip-172-26-10-222 kernel: zDROP ufw-blocklist-input: IN=ens5 OUT= MAC=0a:ff:d3:68:68:11:0a:9b:ae:dc:47:03:08:00 SRC=127.0.0.1 DST=172.26.10.222 LEN=60 TOS=0x08 PREC=0x20 TTL=46 ID=41887 DF PROTO=TCP SPT=57801 DPT=22 WINDOW=29200 RES=0x00 SYN URGP=0"
                tst = False
                print("tst enqueue line")
                msg = message_manager.enqueue(line)
                time.sleep(10)
                sys.exit(0)
                
            # zDROP check, make a copy of the line before we pass it in
            if 'zDROP' in line:
                # send a message to Tasker_ZDROP
                print(f"enqueue line <{line}>")
                msg = message_manager.enqueue(line)
                time.sleep(.01) # priority scheduling in Python3 - What a joke.
                continue
            
            # Now save on our previous entries list
            line_copy = line[:]
            prevs.add_entry(line_copy)

            # combine
            result = prevs.combine()
            if result is not None:
                result = result.strip()
            else:
                logger.fatal("result can't be None")
                sys.exit(0)

            print(f"combine_result: {result}")
            
            # is there an ip address in result ???
            result_copy = result[:]
            found_dict, shortened_str = sjs.shorten_string(result_copy)

            # debug

            logger.debug(f"shortened_str = {shortened_str}")
            
            if 'ip_address' in found_dict:
                ip_address = found_dict['ip_address']
                # debgging info
                #logging.debug(f"ip_address found by shorten_string is {ip_address}")
            else:
                # debgging info
                #logging.debug(f"no ip_address found, skipping line")
                # we are done if there is not ip_address, on to the next line
                continue

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
                if wl.is_whitelisted(ip_address) is True:
                    ip_address_in_whitelist = True
                else:
                    ip_address_in_whitelist = False                    

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
                f"BadDude   : {True if bad_dude_status else 'False'}\n"            
                f"Country   : {country if country is not None else 'n/a'}"
                f"InWhiteLst: {ip_address_in_whitelist if ip_address_in_whitelist is not None else 'n/a'}"
                f"InDB      : In DB: {tmp_flag} Hazard Level: {hazard_level}"
            )
            # and display it
            print(formatted_string)
            print("-" * 50)
        
            if False:
                # if we are debugging,
                if logger.getEffectiveLevel() <= FLAG_DEBUG :
                    # at this point, we'd want to check with ChatGPT to ascertain the hazard_level level
                    # then add to our threat database
                    db.insert_or_update_threat(shortened_str, 1, hazard_level)

            # done processing this line
            continue
        else:
            continue
        
except KeyboardInterrupt:
    logging.error("Script interrupted. Exiting...")
    stop_event.set()
    if worker_thread_id is not None:
        worker_thread_id.join()
finally:
    work_controller.shutdown()
    remove_pid()
    gs.cleanup()
    message_manager.shutdown()
    database_connection_pool.shutdown()
