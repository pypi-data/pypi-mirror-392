
def generate_params_combination(fixed_params,params_pool,num_combinations):
    """
    Generate a specified number of parameter combinations for a given parameter pool

    Parameters:
    fixed_params: dict - Fixed parameter dictionary. These parameters will appear in all combinations.
    params_pool: dict - Parameter pool dictionary. These parameters will be used to generate combinations.
    num_combinations: int - Number of parameter combinations to generate.

    Returns:
    param_combinations: dict - Parameter combinations
    """
    import itertools
    import random

    random.seed(fixed_params['random_state'])

    keys=list(params_pool.keys())
    values=list(params_pool.values())
    all_combinations=list(itertools.product(*values))

    total_combinations=len(all_combinations)
    if num_combinations>=total_combinations:
        selected_indices=range(total_combinations)
    else:
        selected_indices=random.sample(range(total_combinations),num_combinations)

    # Construct the final list of parameter combinations
    param_combinations=[]
    for idx in selected_indices:
        param_dict=dict(zip(keys,all_combinations[idx]))
        combined_params={**fixed_params,**param_dict}
        param_combinations.append(combined_params)

    return param_combinations

def calculate_weighted_bad_capture_rate(scr,label,proportion,weight=None):
    """
    Calculate the top X% capture rate. The top capture rate = the number of bad(label=1) in a given proportion/the total number of (label=1) in the data.

    Parameters:
    scr: pd.Series - Model score.
    label: pd.Series - Binary label.
    proportion: float - Proportion for the top X%.
    weight: pd.Series - Weight

    Returns:
    the top X%  bad capture rate: float
    """

    # Calculate the top capture rate
    import pandas as pd

    # Create data
    df=pd.DataFrame({'score':scr,'label':label})
    if weight is not None:
        df['weight']=weight
    else:
        df['weight']=1

    # Sort in descending order by scr
    df=df.sort_values(by='score',ascending=False)

    # Calculation
    total_weighted_bad=(df['label']*df['weight']).sum()
    if total_weighted_bad<=0:
        return 0.0

    # Determine the cutoff point
    n=len(df)
    k=max(1,int(round(n*proportion)))

    # Calculate the weighted bad for the top k samples
    top_k=df.head(k)
    captured_weighted_bad=(top_k['label']*top_k['weight']).sum()

    return captured_weighted_bad/total_weighted_bad

def calculate_weighted_top_bad_rate(scr,label,proportion,weight=None):
    """
    Calculate the top X% bad(label=1) rate. The top bad rate = the number of bad(label=1) in a given proportion/the total number of records in a given proportion

    Parameters:
    scr: pd.Series - Model score.
    label: pd.Series - Binary label.
    proportion: float - Proportion for the top X%.
    weight: pd.Series - Weight

    Returns:
    the top X%  bad rate: float
    """

    # Calculate top bad rate
    import pandas as pd

    # Create data
    df=pd.DataFrame({'score':scr,'label':label})
    if weight is not None:
        df['weight']=weight
    else:
        df['weight']=1

    # Sort in descending order by scr
    df=df.sort_values(by='score',ascending=False)

    # Determine the cutoff point
    n=len(df)
    k=max(1,int(round(n*proportion)))

    # Calculation
    top_k=df.head(k)
    weighted_bad=(top_k['label']*top_k['weight']).sum()
    weighted_total=top_k['weight'].sum()

    # Deal with 0
    if weighted_total==0:
        return 0.0

    return weighted_bad/weighted_total

def model_performance(model,data,attr_list,label_name,weight_name,top_capture_proportion,top_bad_proportion):
    """
    Calculate model performance in terms of auc,ks,top X% capture rate and top X% bad rate by the sklearn model object.

    Parameters:
    model: sklearn model object
    data: pandas.Dataframe - Dataset to calculate model performance.
    attr_list: list - List of features for the model.
    label_name: str - Name of the target/label column.
    weight_name: str - Name of the weight column.
    top_capture_proportion: list - List of float to calculate top X% capture rate,e.g.,[0.01,0.5]. [] indicates that the capture rate is not calculated.
    top_bad_proportion: list - List of float to calculate top X% bad rate,e.g.,[0.01,0.5]. [] indicates that the bad rate is not calculated.

    Returns:
    auc: float - AUC. It is the default metric.
    ks: float - KS. It is the default metric.
    tdr_list: list - List of top X% capture rate based on the top_capture_proportion.
    tbr_list: list - List of top X% bad rate based on the top_bad_proportion.
    """
    from sklearn import metrics
    import numpy as np

    predicted_scr=model.predict_proba(data[attr_list])[:,1]

    if weight_name is None:
        auc=metrics.roc_auc_score(y_true=data[label_name].to_numpy(),y_score=predicted_scr,sample_weight=None)
        fpr,tpr,_=metrics.roc_curve(y_true=data[label_name].to_numpy(),y_score=predicted_scr,sample_weight=None)
    else:
        auc = metrics.roc_auc_score(y_true=data[label_name].to_numpy(), y_score=predicted_scr, sample_weight=data[weight_name].to_numpy())
        fpr, tpr, _ = metrics.roc_curve(y_true=data[label_name].to_numpy(), y_score=predicted_scr, sample_weight=data[weight_name].to_numpy())

    ks=np.max(np.abs(tpr - fpr))

    if len(top_capture_proportion)==0 and len(top_bad_proportion)==0:
        return auc,ks

    elif len(top_capture_proportion)!=0 and len(top_bad_proportion)==0:
        tdr_list=[]
        for proportion in top_capture_proportion:
            if weight_name is None:
                tdr=calculate_weighted_bad_capture_rate(scr=predicted_scr,label=data[label_name].to_numpy(),proportion=proportion,weight=None)
            else:
                tdr = calculate_weighted_bad_capture_rate(scr=predicted_scr, label=data[label_name].to_numpy(),
                                                          proportion=proportion, weight=data[weight_name].to_numpy())
            tdr_list.append(tdr)
        return auc,ks,tdr_list

    elif len(top_capture_proportion)==0 and len(top_bad_proportion)!=0:
        tbr_list = []
        for bad_proportion in top_bad_proportion:
            if weight_name is None:
                tbr = calculate_weighted_top_bad_rate(scr=predicted_scr, label=data[label_name].to_numpy(),
                                                      proportion=bad_proportion, weight=None)
            else:
                tbr = calculate_weighted_top_bad_rate(scr=predicted_scr, label=data[label_name].to_numpy(),
                                                      proportion=bad_proportion, weight=data[weight_name].to_numpy())
            tbr_list.append(tbr)
        return auc, ks, tbr_list

    elif len(top_capture_proportion)!=0 and len(top_bad_proportion)!=0:
        tdr_list = []
        for proportion in top_capture_proportion:
            if weight_name is None:
                tdr = calculate_weighted_bad_capture_rate(scr=predicted_scr, label=data[label_name].to_numpy(),
                                                          proportion=proportion, weight=None)
            else:
                tdr = calculate_weighted_bad_capture_rate(scr=predicted_scr, label=data[label_name].to_numpy(),
                                                          proportion=proportion, weight=data[weight_name].to_numpy())
            tdr_list.append(tdr)

        tbr_list=[]
        for bad_proportion in top_bad_proportion:
            if weight_name is None:
                tbr=calculate_weighted_top_bad_rate(scr=predicted_scr, label=data[label_name].to_numpy(),
                                                          proportion=bad_proportion, weight=None)
            else:
                tbr = calculate_weighted_top_bad_rate(scr=predicted_scr, label=data[label_name].to_numpy(),
                                                      proportion=bad_proportion, weight=data[weight_name].to_numpy())
            tbr_list.append(tbr)
        return auc,ks,tdr_list,tbr_list

def random_search_lightgbm(train_data,validation_data,oot_dict,attr_list,categorical_attr_list
                           ,weight,label,fixed_params,params_pool,num_models,store_location,model_name,perf_file_name
                           ,top_capture_proportion,top_bad_proportion):
    """
    Use random search to tune the LightGBM classifier model.

    Parameters:
    train_data: pandas.DataFrame - Training data.
    validation_data: pandas.DataFrame - Validation data.
    oot_dict: dict - Dictionary of out-of-time datasets.
    attr_list: list - List of all features to train the model.
    categorical_attr_list: list - List of categorical features to train the model.
    weight: str - Name of the weight column
    label: str - Name of the target/label variable column
    fixed_params: dict - Fixed parameter dictionary for model tuning. These parameters will appear in all combinations.
    params_pool: dict - Parameter pool dictionary for model tuning. These parameters will be used to generate combinations.
    num_models: int - Number of models to generate.
    store_location: str - Location to store the tuned models.
    model_name: str - Name of the model. The serial number will be automatically appended to the end of the name.
    perf_file_name: str - File name for storing the performance of the tuned models.
    top_capture_proportion: list - List of float to calculate top X% capture rate,e.g.,[0.01,0.5]. [] indicates that the capture rate is not calculated.
    top_bad_proportion: list - List of float to calculate top X% bad rate,e.g.,[0.01,0.5]. [] indicates that the bad rate is not calculated.

    Returns:
    None
    """
    import lightgbm as lgb
    import pickle
    import numpy as np
    import pandas as pd

    params_combinations=generate_params_combination(fixed_params=fixed_params,params_pool=params_pool,num_combinations=num_models)

    if weight is None:
        train_weight=None
        val_weight=None
    else:
        train_weight=train_data[weight]
        val_weight=validation_data[weight]

    for i in range(0,num_models):
        print('----> Train the ',i+1,'Model')
        current_params = params_combinations[i].copy()
        eval_metric=current_params['eval_metric']
        del current_params['eval_metric']

        if 'stopping_rounds' in current_params and 'min_delta' in current_params:
            callbacks=[lgb.early_stopping(stopping_rounds=current_params['stopping_rounds'], min_delta=current_params['min_delta'])]
            del current_params['stopping_rounds']
            del current_params['min_delta']
        else:
            callbacks=[]

        architecture=lgb.LGBMClassifier(**current_params)
        model=architecture.fit(X=train_data[attr_list],y=train_data[label]
                               ,sample_weight=train_weight
                               ,eval_set=[(validation_data[attr_list],validation_data[label])]
                               ,eval_names=['validation']
                               ,eval_sample_weight=[val_weight]
                               ,eval_metric=eval_metric
                               ,categorical_feature=categorical_attr_list
                               ,callbacks=callbacks)
        # store the model
        print('----> Store the ',i+1,'Model')
        pickle.dump(model, open(str(store_location+model_name+str(i)+'.pkl'),'wb'))

        # get model performance
        print('----> Caculate the performance of',i+1,'Model')
        data_dict={}
        data_dict['train']=train_data
        data_dict['validation']=validation_data
        if oot_dict:
            data_dict=dict(**data_dict,**oot_dict)
        perf_dict={}
        for dataset in data_dict.keys():
            if len(top_capture_proportion)==0 and len(top_bad_proportion)==0:
                auc,ks=model_performance(model=model,data=data_dict[dataset],attr_list=attr_list,label_name=label,weight_name=weight
                                         ,top_capture_proportion=top_capture_proportion,top_bad_proportion=top_bad_proportion)
                perf_dict[str(dataset)+'_auc']=auc
                perf_dict[str(dataset)+'_ks']=ks
            elif len(top_capture_proportion)!=0 and len(top_bad_proportion)==0:
                auc,ks,tdr_list=model_performance(model=model,data=data_dict[dataset],attr_list=attr_list,label_name=label,weight_name=weight
                                         ,top_capture_proportion=top_capture_proportion,top_bad_proportion=top_bad_proportion)
                perf_dict[str(dataset) + '_auc'] = auc
                perf_dict[str(dataset) + '_ks'] = ks
                for j in range(0,len(top_capture_proportion)):
                    perf_dict[str(str(dataset)+'_top_'+"{:.0%}".format(top_capture_proportion[j])+'_capture_rate')]=tdr_list[j]

            elif len(top_capture_proportion)==0 and len(top_bad_proportion)!=0:
                auc,ks,tbr_list=model_performance(model=model,data=data_dict[dataset],attr_list=attr_list,label_name=label,weight_name=weight
                                         ,top_capture_proportion=top_capture_proportion,top_bad_proportion=top_bad_proportion)
                perf_dict[str(dataset) + '_auc'] = auc
                perf_dict[str(dataset) + '_ks'] = ks
                for p in range(0,len(top_bad_proportion)):
                    perf_dict[str(str(dataset) + '_top_' + "{:.0%}".format(top_bad_proportion[p]) + '_bad_rate')] = tbr_list[p]

            elif len(top_capture_proportion)!=0 and len(top_bad_proportion)!=0:
                auc,ks,tdr_list,tbr_list=model_performance(model=model,data=data_dict[dataset],attr_list=attr_list,label_name=label,weight_name=weight
                                         ,top_capture_proportion=top_capture_proportion,top_bad_proportion=top_bad_proportion)
                perf_dict[str(dataset) + '_auc'] = auc
                perf_dict[str(dataset) + '_ks'] = ks
                for j in range(0, len(top_capture_proportion)):
                    perf_dict[str(str(dataset) + '_top_' + "{:.0%}".format(top_capture_proportion[j]) + '_capture_rate')] = tdr_list[j]
                for p in range(0,len(top_bad_proportion)):
                    perf_dict[str(str(dataset) + '_top_' + "{:.0%}".format(top_bad_proportion[p]) + '_bad_rate')] = tbr_list[p]
        # get model params
        perf_dict['model_name']=model_name+str(i)
        perf_dict['num_features_in']=model.n_features_
        perf_dict['num_nonzero_features']=np.count_nonzero(model.feature_importances_)
        perf_dict['num_trees_real']=model.n_iter_

        print('----> Output the performance of',i+1,'Model')
        perf_dict=dict(**perf_dict,**params_combinations[i])
        fnl_result=pd.DataFrame(perf_dict,index=[0])

        if i==0:
            fnl_result.to_csv(store_location+perf_file_name+'.csv',index=False)
            file_columns_list=list(fnl_result.columns)
        else:
            assert (list(fnl_result.columns)==file_columns_list)
            fnl_result.to_csv(store_location+perf_file_name+'.csv',mode='a',header=False,index=False)

def random_search_xgboost(train_data,validation_data,oot_dict,attr_list,weight,label,fixed_params,params_pool,num_models,store_location,model_name,perf_file_name
                           ,top_capture_proportion,top_bad_proportion):
    """
    Use random search to tune the XGBoost classifier model.

    Parameters:
    train_data: pandas.DataFrame - Training data.
    validation_data: pandas.DataFrame - Validation data.
    oot_dict: dict - Dictionary of out-of-time datasets.
    attr_list: list - List of all features to train the model.
    weight: str - Name of the weight column.
    label: str - Name of the target/label variable column.
    fixed_params: dict - Fixed parameter dictionary for model tuning. These parameters will appear in all combinations.
    params_pool: dict - Parameter pool dictionary for model tuning. These parameters will be used to generate combinations.
    num_models: int - Number of models to generate.
    store_location: str - Location to store the tuned models.
    model_name: str - Name of the model. The serial number will be automatically appended to the end of the name.
    perf_file_name: str - File name for storing the performance of the tuned models.
    top_capture_proportion: list - List of float to calculate top X% capture rate,e.g.,[0.01,0.5]. [] indicates that the capture rate is not calculated.
    top_bad_proportion: list - List of float to calculate top X% bad rate,e.g.,[0.01,0.5]. [] indicates that the bad rate is not calculated.

    Returns:
    None
    """


    import xgboost as xgb
    import pickle
    import numpy as np
    import pandas as pd

    params_combinations = generate_params_combination(fixed_params=fixed_params, params_pool=params_pool,
                                                      num_combinations=num_models)

    if weight is None:
        train_weight = None
        val_weight = None
    else:
        train_weight = train_data[weight]
        val_weight = validation_data[weight]

    for i in range(0,num_models):
        print('----> Train the ',i+1,'Model')
        current_params = params_combinations[i].copy()

        if 'early_stopping_rounds' in current_params:
            callbacks = [xgb.callback.EarlyStopping(rounds=current_params['early_stopping_rounds']
                                                        , metric_name=current_params['eval_metric']
                                                        , save_best=True)]
        else:
            callbacks=[]

        architecture = xgb.XGBClassifier(**current_params, callbacks=callbacks)
        model = architecture.fit(X=train_data[attr_list]
                                 , y=train_data[label]
                                 , sample_weight=train_weight
                                 , eval_set=[(validation_data[attr_list],validation_data[label])]
                                 , verbose=True
                                 , sample_weight_eval_set=[val_weight])
        # store the model
        print('----> Store the ', i + 1, 'Model')
        pickle.dump(model, open(str(store_location + model_name + str(i) + '.pkl'), 'wb'))

        # get model performance
        print('----> Caculate the performance of', i + 1, 'Model')
        data_dict = {}
        data_dict['train'] = train_data
        data_dict['validation'] = validation_data
        if oot_dict:
            data_dict = dict(**data_dict, **oot_dict)
        perf_dict = {}
        for dataset in data_dict.keys():
            if len(top_capture_proportion) == 0 and len(top_bad_proportion) == 0:
                auc, ks = model_performance(model=model, data=data_dict[dataset], attr_list=attr_list, label_name=label,
                                            weight_name=weight
                                            , top_capture_proportion=top_capture_proportion,
                                            top_bad_proportion=top_bad_proportion)
                perf_dict[str(dataset) + '_auc'] = auc
                perf_dict[str(dataset) + '_ks'] = ks

            elif len(top_capture_proportion) != 0 and len(top_bad_proportion) == 0:
                auc, ks, tdr_list = model_performance(model=model, data=data_dict[dataset], attr_list=attr_list,
                                                      label_name=label, weight_name=weight
                                                      , top_capture_proportion=top_capture_proportion,
                                                      top_bad_proportion=top_bad_proportion)
                perf_dict[str(dataset) + '_auc'] = auc
                perf_dict[str(dataset) + '_ks'] = ks
                for j in range(0, len(top_capture_proportion)):
                    perf_dict[str(str(dataset) + '_top_' + "{:.0%}".format(top_capture_proportion[j]) + '_capture_rate')] = tdr_list[j]

            elif len(top_capture_proportion)==0 and len(top_bad_proportion)!=0:
                auc,ks,tbr_list=model_performance(model=model,data=data_dict[dataset],attr_list=attr_list,label_name=label,weight_name=weight
                                         ,top_capture_proportion=top_capture_proportion,top_bad_proportion=top_bad_proportion)
                perf_dict[str(dataset) + '_auc'] = auc
                perf_dict[str(dataset) + '_ks'] = ks
                for p in range(0,len(top_bad_proportion)):
                    perf_dict[str(str(dataset) + '_top_' + "{:.0%}".format(top_bad_proportion[p]) + '_bad_rate')] = tbr_list[p]

            elif len(top_capture_proportion) != 0 and len(top_bad_proportion) != 0:
                auc, ks, tdr_list, tbr_list = model_performance(model=model, data=data_dict[dataset],
                                                                attr_list=attr_list, label_name=label,
                                                                weight_name=weight
                                                                , top_capture_proportion=top_capture_proportion,
                                                                top_bad_proportion=top_bad_proportion)
                perf_dict[str(dataset) + '_auc'] = auc
                perf_dict[str(dataset) + '_ks'] = ks
                for j in range(0, len(top_capture_proportion)):
                    perf_dict[str(str(dataset) + '_top_' + "{:.0%}".format(top_capture_proportion[j]) + '_capture_rate')] = tdr_list[j]
                for p in range(0, len(top_bad_proportion)):
                    perf_dict[str(str(dataset) + '_top_' + "{:.0%}".format(top_bad_proportion[p]) + '_bad_rate')] = tbr_list[p]
        # get model params
        perf_dict['model_name'] = model_name + str(i)
        perf_dict['num_features_in'] = model.n_features_in_
        perf_dict['num_nonzero_features'] = np.count_nonzero(model.feature_importances_)
        perf_dict['num_trees_real'] = model.best_iteration

        print('----> Output the performance of', i + 1, 'Model')
        perf_dict = dict(**perf_dict, **params_combinations[i])
        fnl_result = pd.DataFrame(perf_dict, index=[0])

        if i == 0:
            fnl_result.to_csv(store_location + perf_file_name + '.csv', index=False)
            file_columns_list = list(fnl_result.columns)
        else:
            assert (list(fnl_result.columns) == file_columns_list)
            fnl_result.to_csv(store_location + perf_file_name + '.csv', mode='a', header=False, index=False)

def feature_importance(method,model):
    """
    Calculate the feature importance based on gains.

    Parameters:
    method: str - Methodology('lightgbm' or 'xgboost').
    model: sklearn model object.

    Returns:
    df_imp: pandas.DataFrame - Feature importance for the given model.
    """
    import pandas as pd
    if method == 'lightgbm':
        feature_imp_pct=model.feature_importances_/model.feature_importances_.sum()
        df_imp=pd.DataFrame({
            'feature': model.feature_name_
            ,'importance_ori':model.feature_importances_
            ,'importance_pct':feature_imp_pct
        })
        df_imp=df_imp.sort_values(by='importance_pct', ascending=False).reset_index(drop=True)
        return df_imp
    elif method == 'xgboost':
        var_imp_dict = model.get_booster().get_score(fmap='', importance_type='total_gain')
        df_imp = pd.DataFrame.from_dict(var_imp_dict, orient='index')
        df_imp = df_imp.reset_index(names='feature').rename(columns={0: 'importance_ori'})
        df_imp['importance_pct'] = df_imp['importance_ori'] / df_imp['importance_ori'].sum()
        df_imp = df_imp.sort_values(by='importance_pct', ascending=False).reset_index(drop=True)
        return df_imp

def train_single_model_lightgbm(train_data,validation_data,oot_dict,attr_list,categorical_attr_list
                                ,weight,label,params,store_location,model_name,top_capture_proportion,top_bad_proportion):
    """
    Train a lightgbm classifier model using the given parameters.

    Parameters:
    train_data: pandas.DataFrame - Training data.
    validation_data: pandas.DataFrame - Validation data.
    oot_dict: dict - Dictionary of out-of-time datasets.
    attr_list: list - List of all features to train the model.
    categorical_attr_list: list - List of categorical features to train the model.
    weight: str - Name of the weight column
    label: str - Name of the target/label variable column
    params: dict - Dictionary of model parameters.
    store_location: str - Location to store the tuned models.
    model_name: str - Name of the model.
    top_capture_proportion: list - List of float to calculate top X% capture rate,e.g.,[0.01,0.5]. [] indicates that the capture rate is not calculated.
    top_bad_proportion: list - List of float to calculate top X% bad rate,e.g.,[0.01,0.5]. [] indicates that the bad rate is not calculated.

    Returns:
    fnl_result: pandas.DataFrame - Performance for the model in terms of auc,ks,top X% capture rate,and top X% bad rate when necessary.
    """
    import lightgbm as lgb
    import numpy as np
    import pandas as pd
    import pickle

    print('----> Train the Model')
    if weight is None:
        train_weight=None
        val_weight=None
    else:
        train_weight=train_data[weight]
        val_weight=validation_data[weight]

    current_params=params.copy()
    eval_metric=current_params['eval_metric']
    del current_params['eval_metric']

    if 'stopping_rounds' in current_params and 'min_delta' in current_params:
        callbacks=[lgb.early_stopping(stopping_rounds=current_params['stopping_rounds'], min_delta=current_params['min_delta'])]
        del current_params['stopping_rounds']
        del current_params['min_delta']
    else:
        callbacks=[]

    architecture=lgb.LGBMClassifier(**current_params)
    model=architecture.fit(X=train_data[attr_list]
                           ,y=train_data[label]
                           ,sample_weight=train_weight
                           ,eval_set=[(validation_data[attr_list], validation_data[label])]
                           ,eval_names=['validation']
                           ,eval_sample_weight=[val_weight]
                           ,eval_metric=eval_metric
                           ,categorical_feature=categorical_attr_list
                           ,callbacks=callbacks
                           )
    print('----> Store the Model')
    pickle.dump(model, open(str(store_location + model_name + '.pkl'), 'wb'))

    # get model performance
    print('----> Calculate the Performance of Model')
    data_dict={}
    data_dict['train']=train_data
    data_dict['validation']=validation_data
    if oot_dict:
        data_dict=dict(**data_dict,**oot_dict)

    perf_dict={}
    for dataset in data_dict.keys():
        if len(top_capture_proportion)==0 and len(top_bad_proportion)==0:
            auc,ks=model_performance(model=model,data=data_dict[dataset],attr_list=attr_list,label_name=label,weight_name=weight
                                     ,top_capture_proportion=top_capture_proportion,top_bad_proportion=top_bad_proportion)
            perf_dict[str(dataset) + '_auc'] = auc
            perf_dict[str(dataset) + '_ks'] = ks

        elif len(top_capture_proportion)!=0 and len(top_bad_proportion)==0:
            auc, ks,tdr_list = model_performance(model=model, data=data_dict[dataset], attr_list=attr_list, label_name=label,weight_name=weight
                                        ,top_capture_proportion=top_capture_proportion,top_bad_proportion=top_bad_proportion)
            perf_dict[str(dataset) + '_auc'] = auc
            perf_dict[str(dataset) + '_ks'] = ks
            for j in range(0, len(top_capture_proportion)):
                perf_dict[str(str(dataset)+'_top_'+"{:.0%}".format(top_capture_proportion[j]) + '_capture_rate')] = tdr_list[j]

        elif len(top_capture_proportion) == 0 and len(top_bad_proportion) != 0:
            auc, ks, tbr_list = model_performance(model=model, data=data_dict[dataset], attr_list=attr_list,
                                                  label_name=label, weight_name=weight
                                                  , top_capture_proportion=top_capture_proportion,
                                                  top_bad_proportion=top_bad_proportion)
            perf_dict[str(dataset) + '_auc'] = auc
            perf_dict[str(dataset) + '_ks'] = ks
            for p in range(0, len(top_bad_proportion)):
                perf_dict[str(str(dataset) + '_top_' + "{:.0%}".format(top_bad_proportion[p]) + '_bad_rate')] = tbr_list[p]

        elif len(top_capture_proportion) != 0 and len(top_bad_proportion) != 0:
            auc, ks, tdr_list, tbr_list = model_performance(model=model, data=data_dict[dataset], attr_list=attr_list,label_name=label, weight_name=weight
                                                  ,top_capture_proportion=top_capture_proportion,top_bad_proportion=top_bad_proportion)
            perf_dict[str(dataset) + '_auc'] = auc
            perf_dict[str(dataset) + '_ks'] = ks
            for j in range(0, len(top_capture_proportion)):
                perf_dict[str(str(dataset) + '_top_' + "{:.0%}".format(top_capture_proportion[j]) + '_capture_rate')] = tdr_list[j]
            for p in range(0,len(top_bad_proportion)):
                perf_dict[str(str(dataset) + '_top_' + "{:.0%}".format(top_bad_proportion[p]) + '_bad_rate')] = tbr_list[p]

    # get model params
    perf_dict['model_name']=model_name
    perf_dict['num_features_in']=model.n_features_
    perf_dict['num_nonzero_features']=np.count_nonzero(model.feature_importances_)
    perf_dict['num_trees_real']=model.n_iter_

    print('----> Output the Performance of Model')
    perf_dict=dict(**perf_dict,**params)
    fnl_result=pd.DataFrame(perf_dict,index=[0])

    return fnl_result

def train_single_model_xgboost(train_data,validation_data,oot_dict,attr_list,weight,label,params,store_location,model_name
                           ,top_capture_proportion,top_bad_proportion):
    """
    Train a xgboost classifier model using the given parameters.

    Parameters:
    train_data: pandas.DataFrame - Training data.
    validation_data: pandas.DataFrame - Validation data.
    oot_dict: dict - Dictionary of out-of-time datasets.
    attr_list: list - List of all features to train the model.
    weight: str - Name of the weight column
    label: str - Name of the target/label variable column
    params: dict - Dictionary of model parameters.
    store_location: str - Location to store the tuned models.
    model_name: str - Name of the model.
    top_capture_proportion: list - List of float to calculate top X% capture rate,e.g.,[0.01,0.5]. [] indicates that the capture rate is not calculated.
    top_bad_proportion: list - List of float to calculate top X% bad rate,e.g.,[0.01,0.5]. [] indicates that the bad rate is not calculated.

    Returns:
    fnl_result: pandas.DataFrame - Performance for the model in terms of auc,ks,top X% capture rate,and top X% bad rate when necessary.
    """

    import xgboost as xgb
    import pickle
    import numpy as np
    import pandas as pd

    if weight is None:
        train_weight = None
        val_weight = None
    else:
        train_weight = train_data[weight]
        val_weight = validation_data[weight]

    print('----> Train the Model')
    current_params = params.copy()

    if 'early_stopping_rounds' in current_params:
        callbacks = [xgb.callback.EarlyStopping(rounds=current_params['early_stopping_rounds']
                                                , metric_name=current_params['eval_metric']
                                                , save_best=True)]
    else:
        callbacks = []

    architecture = xgb.XGBClassifier(**current_params, callbacks=callbacks)
    model = architecture.fit(X=train_data[attr_list]
                             , y=train_data[label]
                             , sample_weight=train_weight
                             , eval_set=[(validation_data[attr_list], validation_data[label])]
                             , verbose=True
                             , sample_weight_eval_set=[val_weight])
    # store the model
    print('----> Store the Model')
    pickle.dump(model, open(str(store_location + model_name + '.pkl'), 'wb'))

    # get model performance
    print('----> Caculate the performance of the Model')
    data_dict = {}
    data_dict['train'] = train_data
    data_dict['validation'] = validation_data
    if oot_dict:
        data_dict = dict(**data_dict, **oot_dict)
    perf_dict = {}
    for dataset in data_dict.keys():
        if len(top_capture_proportion) == 0 and len(top_bad_proportion) == 0:
            auc, ks = model_performance(model=model, data=data_dict[dataset], attr_list=attr_list, label_name=label,
                                        weight_name=weight
                                        , top_capture_proportion=top_capture_proportion,
                                        top_bad_proportion=top_bad_proportion)
            perf_dict[str(dataset) + '_auc'] = auc
            perf_dict[str(dataset) + '_ks'] = ks

        elif len(top_capture_proportion) != 0 and len(top_bad_proportion) == 0:
            auc, ks, tdr_list = model_performance(model=model, data=data_dict[dataset], attr_list=attr_list,
                                                  label_name=label, weight_name=weight
                                                  , top_capture_proportion=top_capture_proportion,
                                                  top_bad_proportion=top_bad_proportion)
            perf_dict[str(dataset) + '_auc'] = auc
            perf_dict[str(dataset) + '_ks'] = ks
            for j in range(0, len(top_capture_proportion)):
                perf_dict[str(str(dataset) + '_top_' + "{:.0%}".format(top_capture_proportion[j]) + '_capture_rate')] = \
                tdr_list[j]

        elif len(top_capture_proportion) == 0 and len(top_bad_proportion) != 0:
            auc, ks, tbr_list = model_performance(model=model, data=data_dict[dataset], attr_list=attr_list,
                                                  label_name=label, weight_name=weight
                                                  , top_capture_proportion=top_capture_proportion,
                                                  top_bad_proportion=top_bad_proportion)
            perf_dict[str(dataset) + '_auc'] = auc
            perf_dict[str(dataset) + '_ks'] = ks
            for p in range(0, len(top_bad_proportion)):
                perf_dict[str(str(dataset) + '_top_' + "{:.0%}".format(top_bad_proportion[p]) + '_bad_rate')] = \
                tbr_list[p]

        elif len(top_capture_proportion) != 0 and len(top_bad_proportion) != 0:
            auc, ks, tdr_list, tbr_list = model_performance(model=model, data=data_dict[dataset],
                                                            attr_list=attr_list, label_name=label,
                                                            weight_name=weight
                                                            , top_capture_proportion=top_capture_proportion,
                                                            top_bad_proportion=top_bad_proportion)
            perf_dict[str(dataset) + '_auc'] = auc
            perf_dict[str(dataset) + '_ks'] = ks
            for j in range(0, len(top_capture_proportion)):
                perf_dict[str(str(dataset) + '_top_' + "{:.0%}".format(top_capture_proportion[j]) + '_capture_rate')] = \
                tdr_list[j]
            for p in range(0, len(top_bad_proportion)):
                perf_dict[str(str(dataset) + '_top_' + "{:.0%}".format(top_bad_proportion[p]) + '_bad_rate')] = \
                tbr_list[p]
    # get model params
    perf_dict['model_name'] = model_name
    perf_dict['num_features_in'] = model.n_features_in_
    perf_dict['num_nonzero_features'] = np.count_nonzero(model.feature_importances_)
    perf_dict['num_trees_real'] = model.best_iteration

    print('----> Output the performance of the Model')
    perf_dict = dict(**perf_dict, **params)
    fnl_result = pd.DataFrame(perf_dict, index=[0])

    return fnl_result

def variable_reduction(method,train_data,validation_data,oot_dict,attr_list,categorical_attr_list,weight,label,params
                                ,threshold,min_num_attrs,store_location,model_name,perf_file_name,top_capture_proportion,top_bad_proportion):
    """
    Feature reduction is performed using the given threshold of the feature importance.
    In each iteration, only the most important features meeting the threshold are kept, and the model is trained based on these features.
    The iteration process terminates when the number of features falls below the min_num_attrs.

    Parameters:
    method: str - Methodology('lightgbm' or 'xgboost').
    train_data: pandas.DataFrame - Training data.
    validation_data: pandas.DataFrame - Validation data.
    oot_dict: dict - Dictionary of out-of-time datasets.
    attr_list: list - List of all features to train the model.
    categorical_attr_list: list - List of categorical features to train the model.
    weight: str - Name of the weight column
    label: str - Name of the target/label variable column
    params: dict - Dictionary of model parameters.
    threshold: float - Threshold of the feature importance. Features will be sorted by importance and retained only if their cumulative importance exceeds the threshold in each iteration.
    min_num_attrs: int - Minimum number of features to keep.
    store_location: str - Location to store the models.
    model_name: str - Name of the model. The serial number will be automatically appended to the end of the name.
    perf_file_name: str - File name for storing the performance of the models.
    top_capture_proportion: list - List of float to calculate top X% capture rate,e.g.,[0.01,0.5]. [] indicates that the capture rate is not calculated.
    top_bad_proportion: list - List of float to calculate top X% bad rate,e.g.,[0.01,0.5]. [] indicates that the bad rate is not calculated.

    Returns:
    None
    """


    import pickle

    i=0
    while len(attr_list)>=min_num_attrs:
        if method=='lightgbm':
            perf=train_single_model_lightgbm(train_data=train_data
                                             ,validation_data=validation_data
                                             ,oot_dict=oot_dict
                                             ,attr_list=attr_list
                                             ,categorical_attr_list=categorical_attr_list
                                             ,weight=weight
                                             ,label=label
                                             ,params=params
                                             ,store_location=store_location
                                             ,model_name=model_name+str(i)
                                             ,top_capture_proportion=top_capture_proportion
                                             ,top_bad_proportion=top_bad_proportion)
        elif method=='xgboost':
            perf = train_single_model_xgboost(train_data=train_data
                                              , validation_data=validation_data
                                              , oot_dict=oot_dict
                                              , attr_list=attr_list
                                              , weight=weight
                                              , label=label
                                              , params=params
                                              , store_location=store_location
                                              , model_name=model_name+str(i)
                                              , top_capture_proportion=top_capture_proportion
                                              , top_bad_proportion=top_bad_proportion
                                              )

        if i==0:
            perf.to_csv(store_location+perf_file_name+'.csv',index=False)
            file_columns_list=list(perf.columns)
        else:
            assert (list(perf.columns)==file_columns_list)
            perf.to_csv(store_location+perf_file_name+'.csv',mode='a',header=False,index=False)

        model=pickle.load(open(store_location+model_name+str(i)+'.pkl','rb'))
        var_imp=feature_importance(method=method,model=model)
        var_imp_cum=var_imp['importance_pct'].cumsum()
        attr_list=var_imp.iloc[0:var_imp_cum[var_imp_cum<=threshold].shape[0]]['feature'].to_list()

        if not (categorical_attr_list is None) and len(list(set(attr_list).intersection(set(categorical_attr_list)))) !=0:
            categorical_attr_list=list(set(attr_list).intersection(set(categorical_attr_list)))
        else:
            categorical_attr_list=None

        i=i+1
