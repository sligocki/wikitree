import argparse
import pandas as pd
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-year", type=int, default=0)
    parser.add_argument("--max-year", type=int, default=10000)
    parser.add_argument("--output", type=str)
    parser.add_argument("--version", type=str, default="default", help="Data version to use")
    args = parser.parse_args()

    print("Loading people.parquet...")
    df_people = pd.read_parquet(f'data/version/{args.version}/people.parquet', 
        columns=['user_num', 'wikitree_id', 'gender_code', 'birth_date', 'death_date', 'birth_location', 'death_location', 'father_num', 'mother_num'])
    
    print("Filtering people born in Western Australia...")
    wa_mask = df_people['birth_location'].str.contains('Western Australia', case=False, na=False)
    wa_people = df_people[wa_mask].copy()

    wa_people['birth_year'] = pd.to_datetime(wa_people['birth_date'], errors='coerce').dt.year
    wa_people = wa_people[(wa_people['birth_year'] >= args.min_year) & (wa_people['birth_year'] <= args.max_year)]
    
    print(f"Found {len(wa_people)} people born in WA between {args.min_year} and {args.max_year}.")
    wa_user_nums = set(wa_people['user_num'])

    print("Processing marriages...")
    df_marriages = pd.read_parquet(f'data/version/{args.version}/marriages.parquet', columns=['spouse1', 'spouse2', 'marriage_date'])
    
    m1 = df_marriages[df_marriages['spouse1'].isin(wa_user_nums)].copy()
    m1.rename(columns={'spouse1': 'user_num'}, inplace=True)
    m2 = df_marriages[df_marriages['spouse2'].isin(wa_user_nums)].copy()
    m2.rename(columns={'spouse2': 'user_num'}, inplace=True)
    
    wa_marriages = pd.concat([m1[['user_num', 'marriage_date']], m2[['user_num', 'marriage_date']]])
    wa_marriages['marriage_date'] = pd.to_datetime(wa_marriages['marriage_date'], errors='coerce')
    
    m_stats = wa_marriages.groupby('user_num').agg(
        num_marriages=('marriage_date', 'size'),
        first_marriage_date=('marriage_date', 'min')
    ).reset_index()

    print("Processing children...")
    c_father = df_people[df_people['father_num'].isin(wa_user_nums)][['father_num', 'birth_date']].copy()
    c_father.rename(columns={'father_num': 'user_num'}, inplace=True)
    
    c_mother = df_people[df_people['mother_num'].isin(wa_user_nums)][['mother_num', 'birth_date']].copy()
    c_mother.rename(columns={'mother_num': 'user_num'}, inplace=True)
    
    wa_children = pd.concat([c_father, c_mother])
    wa_children['birth_date'] = pd.to_datetime(wa_children['birth_date'], errors='coerce')
    
    c_stats = wa_children.groupby('user_num').agg(
        num_children=('birth_date', 'size'),
        first_child_born_date=('birth_date', 'min'),
        last_child_born_date=('birth_date', 'max')
    ).reset_index()

    print("Merging data...")
    res = wa_people.merge(m_stats, on='user_num', how='left')
    res = res.merge(c_stats, on='user_num', how='left')
    
    res['num_marriages'] = res['num_marriages'].fillna(0).astype(int)
    res['num_children'] = res['num_children'].fillna(0).astype(int)
    
    res['birth_date'] = pd.to_datetime(res['birth_date'], errors='coerce').dt.strftime('%Y-%m-%d').fillna('')
    res['death_date'] = pd.to_datetime(res['death_date'], errors='coerce').dt.strftime('%Y-%m-%d').fillna('')
    res['first_marriage_date'] = res['first_marriage_date'].dt.strftime('%Y-%m-%d').fillna('')
    res['first_child_born_date'] = res['first_child_born_date'].dt.strftime('%Y-%m-%d').fillna('')
    res['last_child_born_date'] = res['last_child_born_date'].dt.strftime('%Y-%m-%d').fillna('')
    
    cols = [
        'user_num', 'wikitree_id', 'gender_code', 'birth_date', 'death_date',
        'birth_location', 'death_location', 'first_marriage_date', 'num_marriages',
        'first_child_born_date', 'last_child_born_date', 'num_children'
    ]
    res = res[cols]
    
    # Handle gender_code so it displays correctly as integer string or blank
    res['gender_code'] = pd.to_numeric(res['gender_code'], errors='coerce').astype('Int64').astype(str)
    res['gender_code'] = res['gender_code'].replace('<NA>', '')
    
    print(f"Writing to {args.output}...")
    res.to_csv(args.output, sep='\t', index=False)
    print("Done!")

if __name__ == "__main__":
    main()
