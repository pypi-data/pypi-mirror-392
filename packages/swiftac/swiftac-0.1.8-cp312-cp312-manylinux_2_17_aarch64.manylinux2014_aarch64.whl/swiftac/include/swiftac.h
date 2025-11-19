//
// Created by Khurram Javed on 2025-10-09.
//

#ifndef SWIFTAC_H
#define SWIFTAC_H

#include <vector>
#include <random>

class SwiftTDCritic {
    std::vector<int> setOfEligibleItems; // set of eligible items
    std::vector<float> w;
    std::vector<float> z;
    std::vector<float> z_delta;
    std::vector<float> delta_w;

    std::vector<float> h;
    std::vector<float> h_old;
    std::vector<float> h_temp;
    std::vector<float> beta;
    std::vector<float> z_bar;
    std::vector<float> p;

    std::vector<float> last_alpha;


    float v_delta;
    float lambda;
    float epsilon;
    float v_old;
    float meta_step_size;

    float eta;

    float decay;
public:
    SwiftTDCritic(int num_features, float lambda, float alpha, float epsilon, float meta_step_size, float eta,
                  float decay);

    std::pair<float, float> Step(std::vector<int> &feature_indices, float reward, float gamma) ;
};


class SwiftTDActor  {
    std::vector<int> setOfEligibleItems; // set of eligible items
    std::vector<float> w;
    std::vector<float> z;
    std::vector<float> z_delta;
    std::vector<float> delta_w;

    std::vector<float> h;
    std::vector<float> h_old;
    std::vector<float> h_temp;
    std::vector<float> beta;
    std::vector<float> z_bar;
    std::vector<float> p;

    float p_old;

    std::vector<float> last_alpha;
    std::mt19937 gen;

    float lambda;
    float epsilon;
    float meta_step_size;

    float eta;

    float decay;

    float action_prob_bias;
public:
    SwiftTDActor(int num_features, float lambda, float alpha, float epsilon, float meta_step_size, float eta,
                 float decay, float action_prob_at_initialization, int seed);

    bool Step(std::vector<int> &feature_indices, float td_error, float gamma, float v_old) ;
};

class SwiftActorCritic {
    std::vector<SwiftTDActor> actions;
    SwiftTDCritic critic;
public:
    SwiftActorCritic(int num_features, int num_actions, float lambda, float alpha, float epsilon, float meta_step_size,
                     float eta, float eta_actor, float decay, float action_prob_at_init, int seed);

    std::vector<int>  Step(std::vector<int> &feature_indices, float reward, float gamma);
};



#endif //SWIFTAC_H
