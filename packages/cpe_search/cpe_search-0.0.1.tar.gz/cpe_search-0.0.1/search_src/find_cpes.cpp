#include <iostream>
#include <nlohmann/json.hpp>
#include <fstream>
#include <chrono>
#include <algorithm>
#include <string>
#include <cstdlib>
#include <climits>
#include <unordered_set>
#include <unordered_map>

using json = nlohmann::json;
static int nvd_exploit_ref_id = 0;






// def _search_cpes(queries_raw, count, threshold, zero_extend_versions=False, keep_data_in_memory=False):
//     with open(CPE_DICT_FILE, "r") as fout:
//         for line in fout:
//             cpe, cpe_tf, cpe_abs = line.rsplit(';', maxsplit=2)
//             cpe_tf = json.loads(cpe_tf)
//             cpe_abs = float(cpe_abs)

//             for query in queries:
//                 query_tf, query_abs = query_infos[query]
//                 intersecting_words = set(cpe_tf.keys()) & set(query_tf.keys())
//                 inner_product = sum([cpe_tf[w] * query_tf[w] for w in intersecting_words])

//                 normalization_factor = cpe_abs * query_abs

//                 if not normalization_factor:  # avoid divison by 0
//                     continue

//                 sim_score = float(inner_product)/float(normalization_factor)

//                 if threshold > 0 and sim_score < threshold:
//                     continue

//                 cpe_base = ':'.join(cpe.split(':')[:5]) + ':'
//                 if sim_score > most_similar[query][0][1]:
//                     most_similar[query] = [(cpe, sim_score)] + most_similar[query][:count-1]
//                 elif len(most_similar[query]) < count and not most_similar[query][0][0].startswith(cpe_base):
//                     most_similar[query].append((cpe, sim_score))
//                 elif not most_similar[query][0][0].startswith(cpe_base):
//                     insert_idx = None
//                     for i, (cur_cpe, cur_sim_score) in enumerate(most_similar[query][1:]):
//                         if sim_score > cur_sim_score:
//                             if not cur_cpe.startswith(cpe_base):
//                                 insert_idx = i+1
//                             break
//                     if insert_idx:
//                         most_similar[query] = most_similar[query][:insert_idx] + [(cpe, sim_score)] + most_similar[query][insert_idx:-1]





int main(int argc, char *argv[]) {

    if (argc != 3) {
        std::cerr << "Wrong argument count." << std::endl;
        std::cerr << "Usage: ./create_db cve_folder outfile" << std::endl;
        return EXIT_FAILURE;
    }

    std::string cve_folder = argv[1];
    std::string outfile = argv[2];
    std::string filename;
    std::vector<std::string> cve_files;


    catch (std::exception& e) {
        std::cerr << "exception: " << e.what() << std::endl;
        return EXIT_FAILURE;
    }
    auto time = std::chrono::high_resolution_clock::now() - start_time;

    char *db_abs_path = realpath(outfile.c_str(), NULL);
    std::cout << "Database creation took " <<
    (float) (std::chrono::duration_cast<std::chrono::microseconds>(time).count()) / (1e6) << "s .\n";
    std::cout << "Local copy of NVD created as " << db_abs_path << " ." << std::endl;
    free(db_abs_path);
    return EXIT_SUCCESS;
}





