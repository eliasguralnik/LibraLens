import queue


auth_data_queue = queue.Queue()
auth_ui_change_queue = queue.Queue()
logout_process_queue = queue.Queue()
close_command_queue = queue.Queue()

treeview_data_exchange_queue = queue.Queue()
treeview_data_request_answer_queue = queue.Queue()

book_adding_data_exchange_queue = queue.Queue()
book_adding_data_answer_queue = queue.Queue()

student_adding_data_exchange_queue = queue.Queue()
student_adding_data_answer_queue = queue.Queue()

loan_data_adding_queue = queue.Queue()
loan_adding_data_answer_queue = queue.Queue()

return_book_request_queue = queue.Queue()
return_book_answer_queue = queue.Queue()

get_all_red_loans_queue = queue.Queue()
get_all_red_loans_data_queue = queue.Queue()

get_catalog_data_request_queue = queue.Queue()
get_catalog_data_answer_queue = queue.Queue()

send_for_card_barcode_creation_queue = queue.Queue()
get_for_card_barcode_creation_queue = queue.Queue()

prove_if_loan_queue = queue.Queue()
prove_if_loan_ans_queue = queue.Queue()

process_loan_extend_queue = queue.Queue()
process_loan_extend_ans_queue = queue.Queue()

get_all_emails_queue = queue.Queue()
emails_data_queue = queue.Queue()

send_delete_book_queue = queue.Queue()
get_approve_delete_book_queue = queue.Queue()

send_delete_student_queue = queue.Queue()
get_approve_delete_student_queue = queue.Queue()
