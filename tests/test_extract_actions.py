import guidance
from guidance import gen, models, select
from anli.nlu_interface import NLUInterface

# Define potential Kubernetes actions
actions = ['create', 'delete', 'edit']

# use mistral:
nlu_interface = NLUInterface()
# use llama2-7b-chat:
# nlu_interface = NLUInterface('/anli/example_configs/config.yaml')

@guidance
def extract_action(lm, request):
    # Ask the model to identify the action
    lm += f"What action is being requested? '{request}'"
    action = select(actions, name='action')
    lm += action
    # Retrieve the action from the model's state
    # print(lm)
    chosen_action = lm['action']
    # print(chosen_action)
    return chosen_action


@guidance
def extract_object(lm, action, request):
    # Ask the model to identify the Kubernetes object
    lm += f"What Kubernetes object is related to the {action} action in '{request}'?"
    k8s_object = gen(name='object')
    lm += k8s_object
    # Retrieve the object from the model's state
    # print(lm)
    chosen_object = lm['object']
    return chosen_object


# Example usage
lm = nlu_interface.model
request = "Please delete the pod named 'temp-worker' from the system."
action = lm + extract_action(request)
k8s_object = lm + extract_object(action, request)
print(action, k8s_object)
