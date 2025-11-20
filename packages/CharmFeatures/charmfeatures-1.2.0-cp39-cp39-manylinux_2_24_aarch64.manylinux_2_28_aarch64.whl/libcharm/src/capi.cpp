/* capi.cpp */
/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
/*                                                                               */
/* Copyright 2020 Ilya G. Goldberg                                               */
/*                                                                               */
/*                                                                               */
/*                                                                               */
/*    This library is free software; you can redistribute it and/or              */
/*    modify it under the terms of the GNU Lesser General Public                 */
/*    License as published by the Free Software Foundation; either               */
/*    version 2.1 of the License, or (at your option) any later version.         */
/*                                                                               */
/*    This library is distributed in the hope that it will be useful,            */
/*    but WITHOUT ANY WARRANTY; without even the implied warranty of             */
/*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU          */
/*    Lesser General Public License for more details.                            */
/*                                                                               */
/*    You should have received a copy of the GNU Lesser General Public           */
/*    License along with this library; if not, write to the Free Software        */
/*    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA  */
/*                                                                               */
/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
/*                                                                               */
/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
/* Written by:                                                                   */
/*      Ilya G. Goldberg <igg [at] iggtec [dot] com [dot]>                       */
/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
#include <stdexcept>
#include <iostream>
#include <string>
#include "cmatrix.h"
#include "Tasks.h"
#include "libcharm.h"
namespace LC = LibCharm;

extern "C"
const FeatureComputationPlan *get_std_feature_computation_plan (
	const bool color = false, const bool short_features = false)
{

	if (short_features && color)
		return (StdFeatureComputationPlans::getFeatureSetColor());
	else if (short_features && !color)
		return (StdFeatureComputationPlans::getFeatureSet());
	else if (!short_features && color)
		return(StdFeatureComputationPlans::getFeatureSetLongColor());
	else
		return(StdFeatureComputationPlans::getFeatureSetLong());
}


extern "C"
const FeaturePlanExecutor *test_custom_feature_executor ()
{
	size_t n_features = 2;
	char feature_names[][32] = {"Edge Features ()","Otsu Object Features ()"};

	FeatureComputationPlan *the_plan = new FeatureComputationPlan ("test plan");
	if (the_plan) {
		for (size_t i = 0; i < n_features; i++) {
			the_plan->add(feature_names[i]);
		}
	}
	the_plan->feature_vec_type = 0;
	the_plan->finalize();

	FeaturePlanExecutor *executor  = new FeaturePlanExecutor (the_plan);
	return (executor);
}

extern "C"
FeaturePlanExecutor *custom_features_executor (const char *plan_name, const char **feature_names, size_t n_features) {
	FeaturePlanExecutor *executor;

	try {
		LC::resetError();
		FeatureComputationPlan *the_plan = new FeatureComputationPlan (plan_name);
		if (the_plan) {
			for (size_t i = 0; i < n_features; i++) {
				the_plan->add(feature_names[i]);
			}
		}
		the_plan->feature_vec_type = 0;
		the_plan->finalize();
		if (LC::forking_executor)
			executor  = new ForkingFeaturePlanExecutor (the_plan);
		else
			executor  = new FeaturePlanExecutor (the_plan);
	} catch (std::exception &e) {
		LC::catError (e.what());
		std::cerr << LC::getErrorStr();
		return (NULL);
	} catch (...) {
		LC::catError ("unrecognized exception\n");
		std::cerr << LC::getErrorStr();
		return (NULL);
	}

	return (executor);
}

extern "C"
const FeaturePlanExecutor *std_feature_executor (
	const bool color = false, const bool short_features = false)
{
	if (LC::forking_executor)
		return (new ForkingFeaturePlanExecutor (
			get_std_feature_computation_plan(color, short_features))
		);
	else
		return (new FeaturePlanExecutor (
			get_std_feature_computation_plan(color, short_features))
		);
}

extern "C"
void del_executor (FeaturePlanExecutor *executor) {
	// If it's not a standard plan delete that too
	if (executor) {
		if (executor->plan && executor->plan->feature_vec_type == 0)
			delete executor->plan;
		delete executor;
	}
}


extern "C"
int get_features (double *vec_ptr, double *mat_ptr,
	const unsigned int width, const unsigned int height,
	FeaturePlanExecutor *executor)
{
	try {
		LC::resetError();
		ImageMatrix *matrix;
		matrix = new ImageMatrix;

		// N.B.: Color is not supported
		matrix->remap_pix_plane(mat_ptr, width, height);
		executor->run(matrix, vec_ptr, 0);
		// std::cerr << "returned from running features executor" << std::endl;

		// The data pointer doesn't belong to this matrix, so make sure it stays when
		// the matrix goes out of scope.
		matrix->remap_pix_plane(NULL, 0, 0);
		// std::cerr << "remapped pixel vector" << std::endl;

	} catch (std::exception &e) {
		LC::catError (e.what());
		std::cerr << LC::getErrorStr();
		return (-1);
	} catch (...) {
		LC::catError ("unrecognized exception\n");
		std::cerr << LC::getErrorStr();
		return (-1);
	}
	// Should return an error condition of there is one (?)
	return (executor->plan->n_features);
}


extern "C"
const unsigned int get_featurevec_version () {
	return (StdFeatureComputationPlans::feature_vector_major_version);
}


// The array of pointers that's returned is allocated, but the pointers it contains are static
// don't forget to call delete[] names;
extern "C"
const char **get_feature_names (unsigned int *f_count, FeaturePlanExecutor *executor)
{
	const char **names;

	unsigned int count = executor->plan->n_features;
	*f_count = count;
	names = new const char *[count]; 

	for (unsigned int i = 0; i < count; i++)
		names[i] = executor->plan->getFeatureNameByIndex(i).c_str();

	return (names);
}

extern "C"
void del_feature_names (const char **names) {
	// We only need to free the array of pointers.
	// The strings that each of the pointers points to are statics.
	if (names)
		delete[] names;
}

extern "C"
void get_error (char *err_str, size_t max_len) {
	LC::getErrorStr().copy (err_str, max_len);
}

extern "C"
void get_libparam (int *verbosity, bool *forking_executor, bool *forking_haralick, bool *forking_gabor) {
	*verbosity        = LC::verbosity;
	*forking_executor = LC::forking_executor;
	*forking_haralick = LC::forking_haralick;
	*forking_gabor    = LC::forking_gabor;
}

extern "C"
void set_libparam (int verbosity, bool forking_executor, bool forking_haralick, bool forking_gabor) {
	LC::verbosity        = verbosity;
	LC::forking_executor = forking_executor;
	LC::forking_haralick = forking_haralick;
	LC::forking_gabor    = forking_gabor;
}