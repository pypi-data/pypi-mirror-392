#ifndef __LIBCHARM_H__
#define __LIBCHARM_H__
#include <cstdlib>
#include <string>
#include <vector>

namespace LibCharm {

	class Globals {
		public:
			// global variables
			// Note that we are using a singleton with a static instance in a method, so these are
			// instance variables.
			// Verbosity levels:
			// 		0-Classification accuracy and similarity and confusion matrices only
			// 		1-Individual
			// 		2-Everything except the confusion and similarity matrices when printing to std out only
			//      > 3 - report things that are being calculated
			//      > 4 - report algorithms being registered (this is done pre-main, possibly prior to verbosity being set)
			//      > 5 - report execution task execution
			//      > 6 - report execution tasks added/removed from queue
			//      > 7 - report memory allocation/deallocation for matrixes
			static int verbosity;
			static bool forking_executor;
			static bool forking_haralick;
			static bool forking_gabor;
		private:
			Globals() {};                      // Constructor? (the {} brackets) are needed here.
			Globals(Globals const&);        // Don't Implement
			void operator=(Globals const&); // Don't implement
			~Globals() {};                     // Don't implement
	};

	// extern Globals &globals = Globals::instance();

	class Errors {
		public:
			static std::vector<std::string> messages;
			enum ERROR_CODE {
				WC_UNINITIALIZED,
				WC_NO_ERROR,
				WC_IPP_NULL,
				WC_MM_FAIL_RECURSIVE_CALL,
				WC_TRANSFORM_FAIL,
				WC_EMPTY,
				WC_NOT_IMPLEMENTED,
				WC_INPUT_IMAGEMATRIX_NULL
			};
			static void catError (const char *fmt, ...);
			static void catErrorStr (const std::string &error);
			static int showError(int stop, const char *fmt, ...);
			static const std::string getErrorStr ();
			static const char* translateError( ERROR_CODE return_val );
			static void resetError ();
		private:
			// class variable
			static void catErrno ();

			Errors() {}; // private constructor makes this a static class
			Errors(Errors const&); // Don't Implement
			void operator=(Errors const&);  // Don't implement

	};

	// These are just to make access shorter:
	// namespace LibCharm = LC
	// LC::verbosity = 4

	extern int& verbosity;
	extern bool& forking_executor;
	extern bool& forking_haralick;
	extern bool& forking_gabor;

	extern decltype(Errors::catError)& catError;
	extern decltype(Errors::showError)& showError;
	extern decltype(Errors::catErrorStr)& catErrorStr;
	extern decltype(Errors::getErrorStr)& getErrorStr;
	extern decltype(Errors::resetError)& resetError;
}; // namespace LibCharm
#endif // __LIBCHARM_H__
