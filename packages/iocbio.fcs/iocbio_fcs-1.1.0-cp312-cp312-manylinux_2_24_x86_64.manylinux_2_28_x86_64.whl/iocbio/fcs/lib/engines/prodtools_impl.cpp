#include <cstddef>
#include <cstdint>
#include <omp.h>

double
proddot_impl (const int sz, const double *psfpsf,
              const double *x_integ,
              const double *y_integ,
              const double *z_integ,
              const int32_t *x_index,
              const int32_t *y_index,
              const int32_t *z_index)
{
  double result = 0.0;
#pragma omp parallel for reduction(+ : result)
  for (int i = 0; i < sz; ++i)
    {
      result += psfpsf[i] * x_integ[x_index[i]] * y_integ[y_index[i]]
                * z_integ[z_index[i]];
    }
  return result;
}
