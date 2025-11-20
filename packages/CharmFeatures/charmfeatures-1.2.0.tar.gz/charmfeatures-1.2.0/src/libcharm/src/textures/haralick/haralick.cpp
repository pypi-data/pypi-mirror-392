//---------------------------------------------------------------------------

#include <stdlib.h>
#include "haralick.h"
#include "CVIPtexture.h"
#include "libcharm.h"
#include <unistd.h>
namespace LC = LibCharm;

//---------------------------------------------------------------------------
/* haralick
   output -array of double- a pre-allocated array of 28 doubles
*/

void haralick2D(const ImageMatrix &Im, double distance, double *out) {
	unsigned char **p_gray;
	TEXTURE *features;
	int angle, ntextures=13;
	pid_t cpid=0;
	double min[ntextures],max[ntextures],sum[ntextures];
	double min_value,max_value;
	double scale255;
	readOnlyPixels pix_plane = Im.ReadablePixels();
	AnonymousSharedAllocator<double> dbl_alloc;
	double *all_features_p = dbl_alloc.allocate(4*ntextures);
	double (*all_features)[ntextures] = (double (*)[ntextures])all_features_p;

	if (distance <= 0) distance = 1;

	p_gray = new unsigned char *[Im.height];
	for (unsigned int y = 0; y < Im.height; y++)
		p_gray[y] = new unsigned char[Im.width];

	// to keep this method from modifying the const Im, we use GetStats on a local Moments2 object
	Moments2 local_stats;
	Im.GetStats (local_stats);
	min_value = local_stats.min();
	max_value = local_stats.max();

	scale255 = (255.0/(max_value-min_value));
	for (unsigned int y = 0; y < Im.height; y++)
		for (unsigned int x = 0; x < Im.width; x++)
			p_gray[y][x] = (unsigned char)((pix_plane(y,x) - min_value) * scale255);

	for (int idx = 0; idx < 4; idx++) {
		if (LC::forking_haralick)
			cpid = fork();
		if (cpid == 0) { // Child or didn't call fork
			angle = idx * 45;
			features = Extract_Texture_Features((int)distance, angle, p_gray, Im.height,Im.width);
			all_features[idx][ 0] = features->ASM;
			all_features[idx][ 1] = features->contrast;
			all_features[idx][ 2] = features->correlation;
			all_features[idx][ 3] = features->variance;
			all_features[idx][ 4] = features->IDM;
			all_features[idx][ 5] = features->sum_avg;
			all_features[idx][ 6] = features->sum_var;
			all_features[idx][ 7] = features->sum_entropy;
			all_features[idx][ 8] = features->entropy;
			all_features[idx][ 9] = features->diff_var;
			all_features[idx][10] = features->diff_entropy;
			all_features[idx][11] = features->meas_corr1;
			all_features[idx][12] = features->meas_corr2;
			free(features);
			if (LC::forking_haralick && cpid == 0)
				_Exit(EXIT_SUCCESS); // don't call destructors in the child
		}
	}
	if (LC::forking_haralick)
		wait_all_forks();

	for (int a = 0; a < ntextures; a++) {
		min[a] = INF;
		max[a] = -INF;
		sum[a] = 0;
		for (int idx = 0; idx < 4; idx++) {
			sum[a] += all_features[idx][a];
			if (all_features[idx][a] < min[a]) min[a] = all_features[idx][a];
			if (all_features[idx][a] > max[a]) max[a] = all_features[idx][a];
		}
	}

	for (unsigned int y = 0; y < Im.height; y++)
		delete [] p_gray[y];
	delete [] p_gray;
	dbl_alloc.deallocate((double *)all_features_p, 4*ntextures);


	/* copy the values to the output vector in the right output order */
	double temp[ntextures*2];
	for (int a = 0; a < ntextures; a++) {
		temp[a] = sum[a]/4;
		temp[a+ntextures] = max[a]-min[a];
	}

	out[ 0] = temp[ 0];
	out[ 1] = temp[13];
	out[ 2] = temp[ 1];
	out[ 3] = temp[14];
	out[ 4] = temp[ 2];
	out[ 5] = temp[15];
	out[ 6] = temp[ 9];
	out[ 7] = temp[22];
	out[ 8] = temp[10];
	out[ 9] = temp[23];
	out[10] = temp[ 8];
	out[11] = temp[21];
	out[12] = temp[11];
	out[13] = temp[24];
	out[14] = temp[ 4];
	out[15] = temp[17];
	out[16] = temp[12];
	out[17] = temp[25];
	out[18] = temp[ 5];
	out[19] = temp[18];
	out[20] = temp[ 7];
	out[21] = temp[20];
	out[22] = temp[ 6];
	out[23] = temp[19];
	out[24] = temp[ 3];
	out[25] = temp[16];
}
