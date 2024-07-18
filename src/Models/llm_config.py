gpt3_config_list = [
    {
        'model': "gpt-3.5-turbo",
    }
]

gpt4_config_list = [
    {
        'model': "gpt-4o",
    }
]

# These parameters attempt to produce precise reproducible results
temperature = 0
max_tokens = 500
top_p = 0.5
frequency_penalty = 0.1
presence_penalty = 0.1
seed = 53

gpt3_config = {"config_list": gpt3_config_list, 
               "temperature": temperature,
               "max_tokens": max_tokens,
               "top_p": top_p,
               "frequency_penalty": frequency_penalty,
               "presence_penalty": presence_penalty,
               "seed": seed
}

gpt4_config = {"config_list": gpt4_config_list, 
               "temperature": temperature,
               "max_tokens": max_tokens,
               "top_p": top_p,
               "frequency_penalty": frequency_penalty,
               "presence_penalty": presence_penalty,
               "seed": seed
}
