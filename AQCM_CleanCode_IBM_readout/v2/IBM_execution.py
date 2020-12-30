from preparation_measurement import *
from readout_correction import *

def run_experiment(batch, results_probabilities, readout_params):

    target_points = sphere_points(num_pts)
    # Append the results and print them one by one
    for result in batch:
        results_probabilities.append(result)
        coords = (
            target_points[len(results_probabilities) - 1][0],
            target_points[len(results_probabilities) - 1][1])
                
                
        #Readout calibration
        reordered_results = [results_probabilities[-1][i:i+2] for i in range(0,len(results_probabilities[-1])-1,2)]
        corrected_results.append(correct_copies(readout_params, reordered_results))

        #Write corrected results
        write_copying_results(path, backend_identifier, coords, corrected_results)
        write_copying_results(path, backend_identifier, coords, results_probabilities)
                
        print(len(results_probabilities), "/", num_pts)
    
    return results_probabilities
