/*
 *  Copyright 2023 Collate.
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *  http://www.apache.org/licenses/LICENSE-2.0
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */
import { ReactNode } from 'react';
import { Config, ImmutableTree } from 'react-awesome-query-builder';
import { SearchIndex } from '../../../enums/search.enum';

export interface AdvanceSearchProviderProps {
  children: ReactNode;
  isExplorePage?: boolean;
  modalProps?: {
    title?: string;
    subTitle?: string;
  };
  updateURL?: boolean;
}

export interface AdvanceSearchContext {
  queryFilter?: Record<string, unknown>;
  sqlQuery: string;
  onTreeUpdate: (nTree: ImmutableTree, nConfig: Config) => void;
  toggleModal: (show: boolean) => void;
  treeInternal: ImmutableTree;
  config: Config;
  onReset: () => void;
  onResetAllFilters: () => void;
  onUpdateConfig: (config: Config) => void;
  onChangeSearchIndex: (index: SearchIndex | Array<SearchIndex>) => void;
  searchIndex: string | Array<string>;
  onSubmit: () => void;
  modalProps?: {
    title?: string;
    subTitle?: string;
  };
}

export type FilterObject = Record<string, string[]>;
