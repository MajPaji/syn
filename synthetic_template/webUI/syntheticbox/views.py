import json
import pandas as pd

from time import time, sleep

from django.urls import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

import syntheticbox.lib.SyntheticWrapper as wrapper

from .models import DataAnalyzerUI
from .models import save_uploaded_file
from .models import getSizeOfDataset

def index(request):
    #play_data_list = ["adult_reduced","adult_with_missing_values","compas_reduced","customer_churn","risk_score"]
    play_data_list = ["customer_churn","risk_score","stockholm"]
    context = {"passed_play_data": play_data_list}
    # NOTICE: no .csv suffix in current passed file name
    #server_data_names_map = {"adult_reduced": "AR", "adult_with_missing_values": "AM", "compas_reduced": "CR", "customer_churn": "CC","risk_score": "RS"}
    server_data_names_map = {"customer_churn": "CC","risk_score": "RS","stockholm":"SH"}
    # create a time stamp for current uploading
    data_server_path = "./media/"
    play_data_server_path = "./playdata/syntheticbox/"
    cur_time_stamp = str(int(time()*1e7))
    upload_data_size_threshold = 20
    if request.POST:
        if request.FILES:
            # get user upload file
            upload_csvfile = request.FILES['user_upload_data']
            upload_csvfile2 = request.FILES['user_upload_data2']
            join_column = request.POST.get('user_join_column')
            join_type = request.POST.get('user_join_type')
            current_data_name = data_server_path + cur_time_stamp
            current_data_name2 = current_data_name + '2'
            save_uploaded_file(upload_csvfile, current_data_name)
            save_uploaded_file(upload_csvfile2, current_data_name2)
            # get the size of uploaded data
            upload_data_size = getSizeOfDataset(current_data_name)
            context_size = {"passed_play_data": play_data_list, "passed_size_flag":"false"}
            # if upload data size less than the threshold, back to upload page and alert user
            if upload_data_size <= upload_data_size_threshold:
                return render(request, "syntheticbox/index.html", context_size)
            request.session['passed_data_name'] = current_data_name
            request.session['passed_data_name2'] = current_data_name2
            request.session['passed_join_column'] = join_column
            request.session['passed_join_type'] = join_type
        else:
            selected_data = request.POST["dataset_select"]
            # create a copy of current play data set on server to allow differentiate multiple users at the same time
            cur_data = pd.read_csv(play_data_server_path + selected_data + ".csv")
            new_stamped_name = data_server_path + server_data_names_map[selected_data] + cur_time_stamp
            cur_data.to_csv(new_stamped_name + ".csv", index=False)
            request.session['passed_data_name'] = new_stamped_name
        return HttpResponseRedirect(reverse('syntheticbox:proc_data_dash'))
    else:
        return render(request, "syntheticbox/index.html", context)


def proc_data_dash(request):
    passed_data_name = request.session.get('passed_data_name')
    passed_data_name2 = request.session.get('passed_data_name2')
    passed_join_column = request.session.get('passed_join_column')
    passed_join_type = request.session.get('passed_join_type')

    json_cate_info = wrapper.get_dataset_info(passed_data_name + ".csv")
    att_list = json_cate_info["attribute_list"]
    cat_att_list = json_cate_info["categorical_attributes"]
    key_att_list = json_cate_info['candidate_attributes']
    json_data_table = []
    json_header_table = []
    for i in range(len(att_list)):
        json_data_table.append({"data": str(att_list[i])})
        json_header_table.append({"title": str(att_list[i]), "targets": i})
    json_cate_info2 = wrapper.get_dataset_info(passed_data_name2 + ".csv")
    att_list2 = json_cate_info2["attribute_list"]
    cat_att_list2 = json_cate_info2["categorical_attributes"]
    key_att_list2 = json_cate_info2['candidate_attributes']
    for k in range(len(att_list2)):
        #if (str(att_list2[k]) == passed_join_column):
        #    continue
        json_data_table.append({"data": str(att_list2[k])})
        json_header_table.append({"title": str(att_list2[k]), "targets": i + k + 1})
    # request information    
    request.session['passed_json_columns'] = json_data_table
    request.session['passed_column_name'] = att_list
    data_type_list = []
    for i in att_list:
        data_type_list.append(json_cate_info["attribute_datatypes"][i])

    tuple_n = json_cate_info["number_of_tuples"]
    passed_data_size = getSizeOfDataset(passed_data_name)
    context = {"passed_data_name": passed_data_name, 
               "passed_data_name2": passed_data_name2, 
               "passed_json_columns": json_data_table,
               "passed_column_name": att_list, 
               "passed_json_columns_header": json_header_table,
               "passed_cat_atts": cat_att_list, 
               "passed_att_types": data_type_list, 
               "tuple_n": tuple_n,
               "passed_key_atts": key_att_list, 
               "passed_data_size": passed_data_size,
               "passed_join_column": passed_join_column,
               "passed_join_type": passed_join_type}
    return render(request, "syntheticbox/proc_data_dash.html", context)


def proc_json_processing(request):
    passed_data_name = request.session.get('passed_data_name')
    passed_data_name2 = request.session.get('passed_data_name2')
    passed_join_column = request.session.get('passed_join_column')
    passed_join_type = request.session.get('passed_join_type')
    up_data = DataAnalyzerUI()
    up_data.read_dataset_from_csv(passed_data_name, passed_data_name2, passed_join_column, passed_join_type)
    up_data.get_json_data()
    total_json = up_data.json_data
    return HttpResponse(total_json, content_type='application/json')


def res_json_processing(request):
    passed_data_name = request.session.get('passed_data_name')
    up_data = DataAnalyzerUI()
    up_data.read_dataset_from_csv(passed_data_name)
    up_data.get_json_data()
    total_json = up_data.json_data
    return HttpResponse(total_json, content_type='application/json')


def res_json_processing_after(request):
    passed_data_name = request.session.get('passed_data_name')
    up_data = DataAnalyzerUI()
    up_data.read_dataset_from_csv('{}_synthetic_data'.format(passed_data_name))
    up_data.get_json_data()
    total_json = up_data.json_data
    return HttpResponse(total_json, content_type='application/json')


def res_json_processing_plot(request):
    passed_data_name = request.session.get('passed_data_name')
    passed_slicer_field = request.session.get('passed_slicer_field')
    passed_slicer_value = request.session.get('passed_slicer_value')
    print("plot processing: "+str(passed_slicer_field)+":"+str(passed_slicer_value))       
    description_file = passed_data_name + "_plot.json"
    if passed_slicer_field and passed_slicer_field != '':
        synthetic_data_name = passed_data_name + "_synthetic_data.csv"                
        wrapper.get_plot_data(passed_data_name + ".csv", 
                              synthetic_data_name, 
                              description_file, 
                              slicer=passed_slicer_field,
                              value=passed_slicer_value)
    plot_json = wrapper.read_metadata(description_file)
    return HttpResponse(json.dumps(plot_json), content_type='application/json')
    
    
